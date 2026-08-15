"""The runtimes Mires can install into.

Every target exposes the same contract, so the CLI never needs to know which
runtime it is talking to. A target decides where its home is, which asset kinds
it can express, and how to write them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from mires.compatibility import claude, codex, cursor, opencode
from mires.compatibility.models import AssetInventory, InstallReport, ValidationMessage

__all__ = ["ALL_TARGETS", "TARGETS", "Target", "resolve_targets"]

ALL_TARGETS = "all"


@dataclass(frozen=True)
class Target:
    slug: str
    display_name: str
    option: str
    default_home: Callable[[], Path]
    validate: Callable[[AssetInventory], tuple[ValidationMessage, ...]]
    install: Callable[[AssetInventory, Path, bool], InstallReport]

    @property
    def destination(self) -> str:
        return f"--{self.slug}-home"


TARGETS: dict[str, Target] = {
    target.slug: target
    for target in (
        Target(
            slug=codex.SUPPORTED_TARGET,
            display_name=codex.DISPLAY_NAME,
            option="codex_home",
            default_home=codex.default_home,
            validate=codex.validate_codex,
            install=codex.install_codex_assets,
        ),
        Target(
            slug=cursor.SUPPORTED_TARGET,
            display_name=cursor.DISPLAY_NAME,
            option="cursor_home",
            default_home=cursor.default_home,
            validate=cursor.validate_cursor,
            install=cursor.install_cursor_assets,
        ),
        Target(
            slug=claude.SUPPORTED_TARGET,
            display_name=claude.DISPLAY_NAME,
            option="claude_home",
            default_home=claude.default_home,
            validate=claude.validate_claude,
            install=claude.install_claude_assets,
        ),
        Target(
            slug=opencode.SUPPORTED_TARGET,
            display_name=opencode.DISPLAY_NAME,
            option="opencode_home",
            default_home=opencode.default_home,
            validate=opencode.validate_opencode,
            install=opencode.install_opencode_assets,
        ),
    )
}

TARGET_SLUGS = tuple(TARGETS)


def resolve_targets(selection: str) -> tuple[Target, ...]:
    if selection == ALL_TARGETS:
        return tuple(TARGETS.values())
    target = TARGETS.get(selection)
    if target is None:
        known = ", ".join((*TARGET_SLUGS, ALL_TARGETS))
        raise LookupError(f"unsupported target: {selection}. Supported targets: {known}")
    return (target,)
