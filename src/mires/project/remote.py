"""Git transport for project sync.

Mires never invents a protocol here: the sync repository is an ordinary git
repository, so authentication, hosting, and privacy are whatever the user
already configured for git. Mires keeps a clone of it under `~/.mires/sync/` and
treats that clone as a working area for one directory, `<prefix>/<slug>`.

Divergence is left to git. A pull that is not a fast-forward stops with the path
of the clone so the user resolves it there, exactly as they would in any other
repository.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mires.project.models import DEFAULT_BRANCH, DEFAULT_PREFIX, Remote

__all__ = [
    "CONFIG_FILE",
    "HOME_ENV_VAR",
    "REPO_ENV_VAR",
    "GitError",
    "RemoteNotConfiguredError",
    "ResolvedRemote",
    "SyncRepo",
    "open_sync_repo",
    "resolve_remote",
    "sync_home",
]

HOME_ENV_VAR = "MIRES_HOME"
REPO_ENV_VAR = "MIRES_SYNC_REPO"
CONFIG_FILE = "config.yml"
CLONE_DIR = "sync"


class GitError(RuntimeError):
    """A git command failed. The message carries git's own output."""


class RemoteNotConfiguredError(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            "no sync repository configured. Set `project.remote.repo` in .mires/state.yml, "
            f"export {REPO_ENV_VAR}, or add `sync.repo` to ~/.mires/{CONFIG_FILE}."
        )


@dataclass(frozen=True)
class ResolvedRemote:
    repo: str
    branch: str = DEFAULT_BRANCH
    prefix: str = DEFAULT_PREFIX


def sync_home() -> Path:
    """The Mires user directory. Redirectable so a test never touches the real one."""
    override = os.environ.get(HOME_ENV_VAR)
    return Path(override).expanduser() if override else Path.home() / ".mires"


def user_config() -> dict[str, Any]:
    path = sync_home() / CONFIG_FILE
    if not path.is_file():
        return {}
    try:
        document = yaml.safe_load(path.read_text())
    except yaml.YAMLError:
        return {}
    if not isinstance(document, dict):
        return {}
    sync = document.get("sync")
    return sync if isinstance(sync, dict) else {}


def resolve_remote(declared: Remote | None = None, repo_override: str | None = None) -> ResolvedRemote:
    """Resolve the remote from the project state, the environment, then the user config.

    `declared` is absent when the project does not exist locally yet, which is exactly
    the case a first pull has to serve.
    """
    declared = declared or Remote()
    config = user_config()

    repo = repo_override or declared.repo or os.environ.get(REPO_ENV_VAR) or config.get("repo")
    if not isinstance(repo, str) or not repo.strip():
        raise RemoteNotConfiguredError()

    branch = declared.branch if "branch" in declared.model_fields_set else config.get("branch", DEFAULT_BRANCH)
    prefix = declared.prefix if "prefix" in declared.model_fields_set else config.get("prefix", DEFAULT_PREFIX)
    return ResolvedRemote(repo=repo.strip(), branch=str(branch), prefix=str(prefix).strip("/"))


def clone_path(remote: ResolvedRemote) -> Path:
    """A stable, readable directory per remote. The digest keeps two similar URLs apart."""
    readable = re.sub(r"[^A-Za-z0-9._-]+", "-", remote.repo).strip("-")[:64]
    digest = hashlib.sha256(remote.repo.encode()).hexdigest()[:8]
    return sync_home() / CLONE_DIR / f"{readable}-{digest}"


@dataclass(frozen=True)
class SyncRepo:
    """A clone of the sync repository, positioned on the configured branch."""

    path: Path
    remote: ResolvedRemote

    @property
    def projects_root(self) -> Path:
        return self.path / self.remote.prefix if self.remote.prefix else self.path

    def project_path(self, slug: str) -> Path:
        return self.projects_root / slug

    def has_project(self, slug: str) -> bool:
        return self.project_path(slug).is_dir()

    def project_slugs(self) -> list[str]:
        root = self.projects_root
        if not root.is_dir():
            return []
        return sorted(entry.name for entry in root.iterdir() if entry.is_dir() and not entry.name.startswith("."))

    def pending_changes(self, slug: str) -> list[str]:
        """Paths git sees as changed under this project, staged or not, including ignored files."""
        relative = self._relative(slug)
        result = git(["status", "--porcelain", "--untracked-files=all", "--", relative], cwd=self.path)
        return [line[3:].strip() for line in result.stdout.splitlines() if line.strip()]

    def commit_and_push(self, slug: str, message: str) -> bool:
        """Stage, commit, and push this project. Returns False when there was nothing to send."""
        relative = self._relative(slug)
        # Project configuration is routinely ignored by the project's own repository,
        # which is the reason it needs syncing at all, so staging has to be forced.
        git(["add", "--all", "--force", "--", relative], cwd=self.path)
        if git(["diff", "--cached", "--quiet", "--", relative], cwd=self.path, check=False).returncode == 0:
            return False
        git(["commit", "--message", message], cwd=self.path)
        git(["push", "origin", f"HEAD:refs/heads/{self.remote.branch}"], cwd=self.path)
        return True

    def _relative(self, slug: str) -> str:
        return self.project_path(slug).relative_to(self.path).as_posix()


def open_sync_repo(remote: ResolvedRemote, *, refresh: bool = True) -> SyncRepo:
    """Clone the sync repository if it is missing, then bring it up to date."""
    path = clone_path(remote)
    if not (path / ".git").is_dir():
        path.parent.mkdir(parents=True, exist_ok=True)
        git(["clone", remote.repo, str(path)])
        _checkout(path, remote.branch)
        return SyncRepo(path=path, remote=remote)

    repo = SyncRepo(path=path, remote=remote)
    if refresh:
        pull(repo)
    return repo


def pull(repo: SyncRepo) -> None:
    """Fast-forward the clone onto the remote branch, or stop and let the user resolve it."""
    git(["fetch", "origin"], cwd=repo.path)
    _checkout(repo.path, repo.remote.branch)
    if not _has_ref(repo.path, f"origin/{repo.remote.branch}"):
        return
    merged = git(["merge", "--ff-only", f"origin/{repo.remote.branch}"], cwd=repo.path, check=False)
    if merged.returncode != 0:
        raise GitError(
            f"the sync clone has diverged from origin/{repo.remote.branch}. "
            f"Resolve it in {repo.path} and run the command again.\n{merged.stderr.strip()}"
        )


def _checkout(path: Path, branch: str) -> None:
    if _current_branch(path) == branch:
        return
    if _has_ref(path, branch):
        git(["checkout", branch], cwd=path)
        return
    if _has_ref(path, f"origin/{branch}"):
        git(["checkout", "-b", branch, "--track", f"origin/{branch}"], cwd=path)
        return
    git(["checkout", "-B", branch], cwd=path)


def _current_branch(path: Path) -> str:
    return git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, check=False).stdout.strip()


def _has_ref(path: Path, ref: str) -> bool:
    return git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=path, check=False).returncode == 0


def git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", *args]
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, env=env)
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise GitError(f"`{' '.join(command)}` failed: {detail}")
    return result
