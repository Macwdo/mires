from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mires.messages import ValidationMessage

__all__ = [
    "AgentAsset",
    "AssetInventory",
    "HookAsset",
    "InstallReport",
    "McpAsset",
    "RuleAsset",
    "SkillAsset",
    "ValidationMessage",
]


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
class RuleAsset:
    name: str
    description: str
    path: Path

    @property
    def body(self) -> str:
        return self.path.read_text().strip()


@dataclass(frozen=True)
class McpAsset:
    name: str
    description: str
    path: Path
    server: dict[str, Any]

    @property
    def is_remote(self) -> bool:
        return "url" in self.server


@dataclass(frozen=True)
class HookAsset:
    """A hook declared with the canonical Mires event vocabulary.

    `events` maps a canonical event name to the commands bound to it. Each target
    translates those names into whatever its own runtime calls them.
    """

    name: str
    description: str
    path: Path
    events: dict[str, tuple[dict[str, Any], ...]]

    @property
    def directory(self) -> Path:
        return self.path.parent


@dataclass(frozen=True)
class AssetInventory:
    root: Path
    agents: tuple[AgentAsset, ...]
    skills: tuple[SkillAsset, ...]
    rules: tuple[RuleAsset, ...] = ()
    mcps: tuple[McpAsset, ...] = ()
    hooks: tuple[HookAsset, ...] = ()
    specs: tuple[Path, ...] = ()
    errors: tuple[ValidationMessage, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class InstallReport:
    """What an install actually wrote, per asset kind."""

    home: Path
    counts: dict[str, int] = field(default_factory=dict)
    unsupported: tuple[str, ...] = ()

    def summary(self) -> str:
        installed = ", ".join(f"{count} {kind}" for kind, count in self.counts.items() if count)
        return installed or "nothing"
