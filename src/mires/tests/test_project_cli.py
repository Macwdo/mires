from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mires.project.loader import load_project, project_state_path
from mires.project.models import Remote
from mires.project.remote import (
    HOME_ENV_VAR,
    REPO_ENV_VAR,
    clone_path,
    git,
    resolve_remote,
    user_config,
)
from mires.tests.test_project_state import write_project, write_project_skill

SKILL_SECTION = '\nskills:\n  - name: Billing\n    slug: billing\n    description: "Billing"\n'


class RemoteResolutionTests(unittest.TestCase):
    def test_explicit_repo_wins_over_state_env_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            (home / "config.yml").write_text("sync:\n  repo: from-config\n")
            env = {HOME_ENV_VAR: str(home), REPO_ENV_VAR: "from-env"}

            with patch.dict(os.environ, env, clear=False):
                remote = resolve_remote(Remote(repo="from-state"), repo_override="from-flag")

            self.assertEqual(remote.repo, "from-flag")

    def test_state_repo_wins_over_env(self) -> None:
        with patch.dict(os.environ, {REPO_ENV_VAR: "from-env"}, clear=False):
            remote = resolve_remote(Remote(repo="from-state"))

        self.assertEqual(remote.repo, "from-state")

    def test_env_wins_over_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            (home / "config.yml").write_text("sync:\n  repo: from-config\n")
            env = {HOME_ENV_VAR: str(home), REPO_ENV_VAR: "from-env"}

            with patch.dict(os.environ, env, clear=False):
                remote = resolve_remote()

            self.assertEqual(remote.repo, "from-env")

    def test_user_config_is_the_last_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            (home / "config.yml").write_text("sync:\n  repo: from-config\n  branch: trunk\n  prefix: team\n")
            env = {HOME_ENV_VAR: str(home), REPO_ENV_VAR: ""}

            with patch.dict(os.environ, env, clear=False):
                remote = resolve_remote()
                self.assertEqual(user_config()["repo"], "from-config")

            self.assertEqual(remote.repo, "from-config")
            self.assertEqual(remote.branch, "trunk")
            self.assertEqual(remote.prefix, "team")

    def test_clone_paths_keep_similar_urls_apart(self) -> None:
        left = clone_path(resolve_remote(Remote(repo="git@example.com:one/mires.git")))
        right = clone_path(resolve_remote(Remote(repo="git@example.com:two/mires.git")))

        self.assertNotEqual(left, right)


class InitTests(unittest.TestCase):
    def test_init_writes_a_valid_project_state(self) -> None:
        with GitWorkspace() as workspace:
            result = workspace.run("project", "init", "--slug", "demo", "--name", "Demo")

            self.assertEqual(result.returncode, 0, result.stderr)
            state = load_project(workspace.project)
            self.assertEqual(state.project.slug, "demo")
            self.assertEqual(state.project.name, "Demo")
            self.assertTrue(project_state_path(workspace.project).is_file())

    def test_init_refuses_to_overwrite(self) -> None:
        with GitWorkspace() as workspace:
            workspace.run("project", "init", "--slug", "demo")
            result = workspace.run("project", "init", "--slug", "demo")

            self.assertEqual(result.returncode, 1)
            self.assertIn("already exists", result.stderr)


class ProjectCliTests(unittest.TestCase):
    def test_push_creates_the_project_in_an_empty_sync_repository(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            result = workspace.run("project", "push")

            self.assertEqual(result.returncode, 0, result.stderr)
            listing = workspace.run("project", "list")
            self.assertIn("- demo", listing.stdout)

    def test_pull_materializes_a_project_that_does_not_exist_locally(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            self.assertEqual(workspace.run("project", "push").returncode, 0)

            empty = workspace.root / "other"
            empty.mkdir()
            result = workspace.run("project", "pull", "--slug", "demo", cwd=empty)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((empty / "AGENTS.md").read_text(), "agents\n")
            self.assertTrue((empty / ".mires" / "skills" / "billing" / "SKILL.md").is_file())
            self.assertFalse((empty / "src" / "app.py").exists())

    def test_project_sync_alias_pulls_when_the_project_is_missing_locally(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            self.assertEqual(workspace.run("project", "push").returncode, 0)

            empty = workspace.root / "other"
            empty.mkdir()
            result = workspace.run("project-sync", "--slug", "demo", cwd=empty)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((empty / "AGENTS.md").is_file())

    def test_a_round_trip_is_idempotent(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            self.assertEqual(workspace.run("project", "push").returncode, 0)

            second = workspace.run("project", "push")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("already matches", second.stdout)

            status = workspace.run("project", "status")
            self.assertIn("In sync.", status.stdout)

    def test_dropping_an_include_removes_it_from_the_sync_repository(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project(include=("AGENTS.md", "NOTES.md"))
            (workspace.project / "NOTES.md").write_text("notes\n")
            self.assertEqual(workspace.run("project", "push").returncode, 0)

            write_project(
                workspace.project,
                include=("AGENTS.md",),
                repo=str(workspace.bare),
                sections=SKILL_SECTION,
            )
            result = workspace.run("project", "push")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("removed NOTES.md", result.stdout)
            self.assertFalse(workspace.remote_project_file("NOTES.md").exists())

    def test_a_push_refuses_files_that_look_like_secrets(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project(include=("AGENTS.md", ".env"))
            (workspace.project / ".env").write_text("TOKEN=live\n")
            result = workspace.run("project", "push")

            self.assertEqual(result.returncode, 1)
            self.assertIn("refusing to sync files that look like secrets", result.stderr)
            self.assertIn(".env", result.stderr)

    def test_a_dry_run_writes_nothing(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            result = workspace.run("project", "push", "--dry-run")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Would sync", result.stdout)
            listing = workspace.run("project", "list")
            self.assertIn("No projects", listing.stdout)

    def test_sync_refuses_to_choose_when_both_sides_moved(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            self.assertEqual(workspace.run("project", "push").returncode, 0)

            (workspace.project / "AGENTS.md").write_text("local\n")
            workspace.change_remote_file("AGENTS.md", "remote\n")

            result = workspace.run("project", "sync")

            self.assertEqual(result.returncode, 1)
            self.assertIn("Both sides", result.stderr)
            self.assertIn("--pull", result.stderr)
            self.assertIn("--push", result.stderr)

    def test_sync_pull_lets_the_repository_win(self) -> None:
        with GitWorkspace() as workspace:
            workspace.seed_project()
            self.assertEqual(workspace.run("project", "push").returncode, 0)
            (workspace.project / "AGENTS.md").write_text("local\n")
            workspace.change_remote_file("AGENTS.md", "remote\n")

            result = workspace.run("project", "sync", "--pull")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((workspace.project / "AGENTS.md").read_text(), "remote\n")


class GitWorkspace:
    """A throwaway project, a bare sync repository, and a redirected Mires home."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="mires-cli-")
        self.root = Path(self._temporary.name)
        self.home = self.root / "home"
        self.bare = self.root / "remote.git"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()
        (self.project / "src").mkdir()
        (self.project / "src" / "app.py").write_text("print('not synced')\n")
        seed_bare(self.bare)

    def __enter__(self) -> GitWorkspace:
        return self

    def __exit__(self, *exception: object) -> None:
        self._temporary.cleanup()

    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                HOME_ENV_VAR: str(self.home),
                REPO_ENV_VAR: str(self.bare),
                "GIT_AUTHOR_NAME": "Mires Tests",
                "GIT_AUTHOR_EMAIL": "mires@example.test",
                "GIT_COMMITTER_NAME": "Mires Tests",
                "GIT_COMMITTER_EMAIL": "mires@example.test",
                "GIT_TERMINAL_PROMPT": "0",
            }
        )
        return env

    def run(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "mires.cli", *arguments],
            cwd=cwd or self.project,
            env=self.env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def seed_project(self, include: tuple[str, ...] = ("AGENTS.md",)) -> None:
        write_project(self.project, include=include, repo=str(self.bare), sections=SKILL_SECTION)
        write_project_skill(self.project, "billing")
        for path in include:
            target = self.project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(f"{path}\n" if path != "AGENTS.md" else "agents\n")

    def remote_project_file(self, relative: str) -> Path:
        remote = resolve_remote(Remote(repo=str(self.bare)))
        with patch.dict(os.environ, {HOME_ENV_VAR: str(self.home)}, clear=False):
            return clone_path(remote) / "projects" / "demo" / relative

    def change_remote_file(self, relative: str, content: str) -> None:
        """Commit a change in a separate clone so the next sync sees remote drift."""
        with tempfile.TemporaryDirectory(prefix="mires-other-") as temp_dir:
            work = Path(temp_dir)
            git(["clone", str(self.bare), str(work)])
            path = work / "projects" / "demo" / relative
            path.write_text(content)
            git(["add", "--force", "--", path.relative_to(work).as_posix()], cwd=work)
            git(
                [
                    "-c",
                    "user.name=Mires Tests",
                    "-c",
                    "user.email=mires@example.test",
                    "commit",
                    "--message",
                    "edit from elsewhere",
                ],
                cwd=work,
            )
            git(["push", "origin", "HEAD:refs/heads/main"], cwd=work)


def seed_bare(path: Path) -> None:
    git(["init", "--bare", "--initial-branch=main", str(path)])
    with tempfile.TemporaryDirectory(prefix="mires-seed-") as temp_dir:
        work = Path(temp_dir)
        git(["clone", str(path), str(work)])
        (work / "README.md").write_text("Mires project sync\n")
        git(["add", "README.md"], cwd=work)
        git(
            [
                "-c",
                "user.name=Mires Tests",
                "-c",
                "user.email=mires@example.test",
                "commit",
                "--message",
                "initial",
            ],
            cwd=work,
        )
        git(["push", "origin", "HEAD:refs/heads/main"], cwd=work)


if __name__ == "__main__":
    unittest.main()
