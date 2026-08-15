"""Locating the catalog Mires should install from.

Mires runs two ways: from a clone of the repository, and straight from the
published package with no clone at all. The catalog is shipped inside the wheel,
so a resolved root is either the working repository or that bundled copy.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["BUNDLED_ROOT", "STATE_FILE", "CatalogNotFoundError", "resolve_root"]

STATE_FILE = "state.yml"
ROOT_ENV_VAR = "MIRES_ROOT"
BUNDLED_ROOT = Path(__file__).resolve().parent / "_catalog"


class CatalogNotFoundError(RuntimeError):
    def __init__(self, searched: tuple[Path, ...]) -> None:
        locations = "\n".join(f"- {path}" for path in searched)
        super().__init__(f"could not find a Mires catalog. Looked for {STATE_FILE} in:\n{locations}")
        self.searched = searched


def resolve_root(explicit: Path | None = None, start: Path | None = None) -> Path:
    """Resolve the catalog root, preferring an explicit choice, then a clone, then the bundled copy."""
    searched: list[Path] = []

    for candidate in _candidates(explicit, start):
        searched.append(candidate)
        if (candidate / STATE_FILE).is_file():
            return candidate.resolve()

    raise CatalogNotFoundError(tuple(searched))


def _candidates(explicit: Path | None, start: Path | None) -> list[Path]:
    if explicit is not None:
        return [explicit.expanduser()]

    candidates: list[Path] = []
    from_env = os.environ.get(ROOT_ENV_VAR)
    if from_env:
        candidates.append(Path(from_env).expanduser())

    working = (start or Path.cwd()).resolve()
    candidates.extend([working, *working.parents])
    candidates.append(BUNDLED_ROOT)
    return candidates
