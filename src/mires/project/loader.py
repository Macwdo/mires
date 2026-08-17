"""Locating, loading, and validating a project.

A project is found the same way a git repository is: by walking up from the
working directory until `.mires/state.yml` appears. Catalog entries declared in
that file live under `.mires/`, so validation runs against that directory rather
than the project root.
"""

from __future__ import annotations

from pathlib import Path

from mires.messages import ValidationMessage
from mires.project.models import PROJECT_DIR, ProjectState
from mires.state.loader import STATE_FILE, StateFileError, read_state
from mires.state.validate import validate_state

__all__ = [
    "ProjectNotFoundError",
    "StateFileError",
    "catalog_root",
    "find_project_root",
    "load_project",
    "project_state_path",
    "validate_project",
]


class ProjectNotFoundError(RuntimeError):
    def __init__(self, start: Path) -> None:
        super().__init__(
            f"no Mires project found in {start} or any parent directory. "
            f"Run `mires project init` to create {PROJECT_DIR}/{STATE_FILE}."
        )
        self.start = start


def catalog_root(root: Path) -> Path:
    """Where a project keeps the assets its state declares."""
    return root / PROJECT_DIR


def project_state_path(root: Path) -> Path:
    return catalog_root(root) / STATE_FILE


def find_project_root(start: Path | None = None) -> Path:
    working = (start or Path.cwd()).resolve()
    for candidate in (working, *working.parents):
        if (candidate / PROJECT_DIR / STATE_FILE).is_file():
            return candidate
    raise ProjectNotFoundError(working)


def load_project(root: Path) -> ProjectState:
    return read_state(project_state_path(root), ProjectState)


def validate_project(root: Path, state: ProjectState) -> tuple[ValidationMessage, ...]:
    errors = list(validate_state(catalog_root(root), state, enforce_skill_visibility=False))
    errors.extend(_check_includes(root, state))
    return tuple(errors)


def _check_includes(root: Path, state: ProjectState) -> list[ValidationMessage]:
    """Includes are already relative and free of `..`; the remaining risk is a symlink out of the project."""
    resolved_root = root.resolve()
    errors: list[ValidationMessage] = []
    for include in state.project.include:
        path = root / include
        if not path.exists():
            continue
        if not path.resolve().is_relative_to(resolved_root):
            errors.append(ValidationMessage(path, "include resolves outside the project root"))
    return errors
