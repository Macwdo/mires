"""Moving a project payload between the working tree and the sync repository.

The payload is exactly what `.mires/state.yml` declares: the state file itself,
every catalog entry it lists, and every `include` path. Nothing else is read or
written, so a project's source code never reaches the sync repository.

Both sides use the same project-relative layout, which makes a direction nothing
more than a choice of source and destination. Each side is overwritten
completely for the paths it owns, and `sync-manifest.json` records the payload of
the last sync: which paths moved, so a path dropped from the state is deleted on
the next run, and what they contained, so the next run can tell which side moved
since then.
"""

from __future__ import annotations

import filecmp
import fnmatch
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from mires.project.models import PROJECT_DIR, ProjectState
from mires.state.loader import STATE_FILE
from mires.state.models import SECTIONS

__all__ = [
    "MANIFEST_FILE",
    "PULL",
    "PUSH",
    "SecretsRefusedError",
    "SyncManifest",
    "SyncReport",
    "compare",
    "digests",
    "drifted",
    "payload_paths",
    "transfer",
]

PULL = "pull"
PUSH = "push"

MANIFEST_FILE = "sync-manifest.json"
MANIFEST_VERSION = 1
GENERATED_NOTICE = "Written by `mires project sync`. It records what the last sync moved."

# Directory noise no project needs to ship, and that would make a sync enormous.
IGNORED_NAMES = (".git", "node_modules", "__pycache__", ".DS_Store", "*.pyc")

# Syncing exists to carry files the project's own repository ignores, which is exactly
# where credentials tend to hide. Refuse them by default rather than commit them.
SECRET_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa*",
    "id_ed25519*",
    "credentials.json",
)


class SecretsRefusedError(RuntimeError):
    def __init__(self, paths: tuple[str, ...]) -> None:
        listed = "\n".join(f"- {path}" for path in paths)
        super().__init__(f"refusing to sync files that look like secrets:\n{listed}")
        self.paths = paths


@dataclass(frozen=True)
class SyncReport:
    direction: str
    slug: str
    source: Path
    destination: Path
    created: tuple[str, ...] = ()
    updated: tuple[str, ...] = ()
    unchanged: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    dry_run: bool = False

    @property
    def written(self) -> tuple[str, ...]:
        return self.created + self.updated

    @property
    def changed(self) -> bool:
        return bool(self.created or self.updated or self.removed)

    @property
    def other_side(self) -> Path:
        """The side that is not the local project: where a pull reads from and a push writes to."""
        return self.source if self.direction == PULL else self.destination

    def summary(self) -> str:
        return (
            f"{len(self.written)} written, {len(self.unchanged)} unchanged, {len(self.removed)} removed"
        )


@dataclass
class SyncManifest:
    """The payload of the last successful sync, kept beside the project state.

    It is the common ancestor of the two sides: the recorded digests are what both
    sides held when they last agreed, so a later run can tell which of them moved.
    """

    root: Path
    recorded: dict[str, str]

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(self.recorded)

    @classmethod
    def load(cls, root: Path) -> SyncManifest:
        path = manifest_path(root)
        if not path.is_file():
            return cls(root=root, recorded={})
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError:
            return cls(root=root, recorded={})
        if not isinstance(document, dict) or document.get("version") != MANIFEST_VERSION:
            return cls(root=root, recorded={})
        paths = document.get("paths")
        if not isinstance(paths, dict):
            return cls(root=root, recorded={})
        return cls(root=root, recorded={str(key): str(value) for key, value in paths.items()})

    def save(self, slug: str, recorded: dict[str, str]) -> None:
        path = manifest_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": MANIFEST_VERSION,
            "notice": GENERATED_NOTICE,
            "slug": slug,
            "paths": dict(sorted(recorded.items())),
        }
        path.write_text(json.dumps(document, indent=2) + "\n")
        self.recorded = dict(recorded)


def manifest_path(root: Path) -> Path:
    return root / PROJECT_DIR / MANIFEST_FILE


def payload_paths(state: ProjectState) -> tuple[str, ...]:
    """Every project-relative path the state declares, in a stable order."""
    paths = [f"{PROJECT_DIR}/{STATE_FILE}"]
    for section in SECTIONS:
        for entry in state.entries(section.field):
            paths.append(f"{PROJECT_DIR}/{state.entry_path(section.field, entry)}")
    paths.extend(state.project.include)
    return tuple(dict.fromkeys(paths))


def transfer(
    state: ProjectState,
    source: Path,
    destination: Path,
    *,
    direction: str,
    previous: tuple[str, ...] = (),
    dry_run: bool = False,
    allow_secrets: bool = False,
) -> SyncReport:
    """Copy the declared payload from `source` to `destination` and prune what the state dropped."""
    declared = payload_paths(state)
    present = tuple(path for path in declared if (source / path).exists())
    missing = tuple(path for path in declared if path not in present)

    if direction == PUSH and not allow_secrets:
        refused = secret_files(source, present)
        if refused:
            raise SecretsRefusedError(refused)

    created = tuple(path for path in present if not (destination / path).exists())
    rest = tuple(path for path in present if path not in set(created))
    updated = tuple(path for path in rest if not same_entry(source / path, destination / path))
    unchanged = tuple(path for path in rest if path not in set(updated))

    stale = tuple(path for path in previous if path not in set(declared))
    removed = tuple(path for path in stale if (destination / path).exists())

    report = SyncReport(
        direction=direction,
        slug=state.project.slug,
        source=source,
        destination=destination,
        created=created,
        updated=updated,
        unchanged=unchanged,
        missing=missing,
        removed=removed,
        dry_run=dry_run,
    )
    if dry_run:
        return report

    for path in report.written:
        copy_entry(source / path, destination / path)
    for path in removed:
        delete_entry(destination / path)
    return report


def digests(paths: tuple[str, ...], root: Path) -> dict[str, str]:
    """Content digest per declared path, which is what the manifest records."""
    return {path: entry_digest(root / path) for path in paths}


def drifted(paths: tuple[str, ...], root: Path, recorded: dict[str, str]) -> tuple[str, ...]:
    """Declared paths whose content on this side no longer matches the last sync."""
    current = digests(paths, root)
    moved = [path for path, digest in current.items() if digest != recorded.get(path, "")]
    moved.extend(path for path, digest in recorded.items() if path not in current and digest)
    return tuple(sorted(set(moved)))


def entry_digest(path: Path) -> str:
    """A digest of a file or of a whole directory. An absent path digests to the empty string."""
    if not path.exists() and not path.is_symlink():
        return ""
    hasher = hashlib.sha256()
    if path.is_dir() and not path.is_symlink():
        for candidate in walk_files(path):
            hasher.update(candidate.relative_to(path).as_posix().encode())
            hasher.update(b"\0")
            hasher.update(_content(candidate))
            hasher.update(b"\0")
        return hasher.hexdigest()
    hasher.update(_content(path))
    return hasher.hexdigest()


def _content(path: Path) -> bytes:
    if path.is_symlink():
        return os.readlink(path).encode()
    try:
        return path.read_bytes()
    except OSError:
        return b""


def compare(
    paths: tuple[str, ...],
    local: Path,
    remote: Path,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Split declared paths into those only local, only remote, and differing on both sides."""
    only_local: list[str] = []
    only_remote: list[str] = []
    differing: list[str] = []
    for path in paths:
        here = local / path
        there = remote / path
        if here.exists() and not there.exists():
            only_local.append(path)
        elif there.exists() and not here.exists():
            only_remote.append(path)
        elif here.exists() and there.exists() and not same_entry(here, there):
            differing.append(path)
    return tuple(only_local), tuple(only_remote), tuple(differing)


def secret_files(root: Path, paths: tuple[str, ...]) -> tuple[str, ...]:
    refused: list[str] = []
    for path in paths:
        for candidate in walk_files(root / path):
            if any(fnmatch.fnmatch(candidate.name, pattern) for pattern in SECRET_PATTERNS):
                refused.append(candidate.relative_to(root).as_posix())
    return tuple(sorted(refused))


def walk_files(path: Path) -> list[Path]:
    if path.is_symlink() or path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file() and not any(_ignored(part) for part in candidate.relative_to(path).parts)
    )


def copy_entry(source: Path, destination: Path) -> None:
    """Replace the destination with the source, so a removed file inside a directory does not survive."""
    delete_entry(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir() and not source.is_symlink():
        shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns(*IGNORED_NAMES))
        return
    shutil.copy2(source, destination, follow_symlinks=False)


def delete_entry(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def same_entry(left: Path, right: Path) -> bool:
    if left.is_dir() != right.is_dir():
        return False
    if left.is_file():
        return filecmp.cmp(left, right, shallow=False)
    left_files = {path.relative_to(left).as_posix(): path for path in walk_files(left)}
    right_files = {path.relative_to(right).as_posix(): path for path in walk_files(right)}
    if left_files.keys() != right_files.keys():
        return False
    return all(filecmp.cmp(left_files[name], right_files[name], shallow=False) for name in left_files)


def _ignored(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in IGNORED_NAMES)
