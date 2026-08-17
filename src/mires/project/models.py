"""The shape of a project state definition.

A project is any directory holding `.mires/state.yml`. That file reuses the
catalog schema, so a project can declare its own skills, subagents, rules, MCP
servers, and hooks, and adds a `project` section describing what else belongs to
the project and which repository it syncs with.

`include` exists because most project configuration already lives where a tool
expects it, often ignored by the project's own git repository. Those paths are
mirrored verbatim instead of being rendered, so a pull puts them back exactly
where the tool reads them.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from pydantic import field_validator

from mires.state.models import MiresState, Slug, StateModel, Text

__all__ = [
    "DEFAULT_BRANCH",
    "DEFAULT_PREFIX",
    "PROJECT_DIR",
    "ProjectConfig",
    "ProjectState",
    "Remote",
    "normalize_include",
]

PROJECT_DIR = ".mires"
DEFAULT_BRANCH = "main"
DEFAULT_PREFIX = "projects"

# `.mires` always travels with the project, and `.git` is the project's own history.
# Declaring either would either duplicate the payload or ship a repository inside a repository.
RESERVED_INCLUDES = (PROJECT_DIR, ".git")


class Remote(StateModel):
    """Where a project synchronizes. Any git repository works, private or not."""

    repo: str | None = None
    branch: str = DEFAULT_BRANCH
    prefix: str = DEFAULT_PREFIX


class ProjectConfig(StateModel):
    name: Text
    slug: Slug
    remote: Remote = Remote()
    include: list[str] = []

    @field_validator("include")
    @classmethod
    def _normalize_includes(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for raw in value:
            candidate = normalize_include(raw)
            if candidate in seen:
                raise ValueError(f"duplicate include: {candidate}")
            seen.add(candidate)
            normalized.append(candidate)
        return normalized


class ProjectState(MiresState):
    project: ProjectConfig


def normalize_include(raw: str) -> str:
    """Reduce an include to a project-relative POSIX path, rejecting anything that escapes the project."""
    candidate = raw.strip().replace("\\", "/").rstrip("/")
    if not candidate:
        raise ValueError("include must not be empty")
    if candidate.startswith("~"):
        raise ValueError(f"include must be relative to the project root: {raw}")

    path = PurePosixPath(candidate)
    if path.is_absolute():
        raise ValueError(f"include must be relative to the project root: {raw}")

    parts = path.parts
    if not parts:
        raise ValueError("include must not be the project root")
    if ".." in parts:
        raise ValueError(f"include must not escape the project root: {raw}")
    for reserved in RESERVED_INCLUDES:
        if reserved in parts:
            raise ValueError(f"include must not cover {reserved}: {raw}")
    return path.as_posix()
