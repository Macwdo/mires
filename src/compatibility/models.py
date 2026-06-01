from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationMessage:
    path: Path
    message: str

    def format(self, root: Path) -> str:
        try:
            display_path = self.path.relative_to(root)
        except ValueError:
            display_path = self.path
        return f"{display_path}: {self.message}"


@dataclass(frozen=True)
class AgentAsset:
    name: str
    description: str
    parent: str
    children: tuple[str, ...]
    path: Path
    metadata_path: Path | None
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SkillAsset:
    name: str
    description: str
    path: Path
    reference_paths: tuple[Path, ...]


@dataclass(frozen=True)
class AssetInventory:
    root: Path
    agents: tuple[AgentAsset, ...]
    skills: tuple[SkillAsset, ...]
    errors: tuple[ValidationMessage, ...]

    @property
    def ok(self) -> bool:
        return not self.errors

