#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from compatibility.codex import SUPPORTED_TARGET as CODEX_TARGET
from compatibility.codex import install_codex_agents, validate_codex
from compatibility.models import AssetInventory, ValidationMessage
from compatibility.opencode import SUPPORTED_TARGET as OPENCODE_TARGET
from compatibility.opencode import install_opencode_assets, validate_opencode
from compatibility.parsing import load_inventory


SUPPORTED_TARGETS = (CODEX_TARGET, OPENCODE_TARGET)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or install runtime compatibility for canonical Mires .ai assets."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=["check", "install"],
        help="Compatibility operation to run.",
    )
    parser.add_argument(
        "--target",
        default=CODEX_TARGET,
        help=f"Runtime target to validate. Supported: {', '.join(SUPPORTED_TARGETS)}.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex home directory for install. Defaults to $HOME/.codex.",
    )
    parser.add_argument(
        "--opencode-home",
        type=Path,
        default=Path.home() / ".config" / "opencode",
        help="OpenCode config directory for install. Defaults to $HOME/.config/opencode.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview install output without writing files.",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    target_errors = check_target_supported(args.target, root)
    if target_errors:
        for error in target_errors:
            print(error.format(root), file=sys.stderr)
        return 2

    inventory = load_inventory(root)
    errors = validate_target(args.target, inventory)
    if errors:
        print(f"Compatibility {args.command} failed for target '{args.target}'.", file=sys.stderr)
        for error in errors:
            print(f"- {error.format(root)}", file=sys.stderr)
        return 1

    if args.command == "install":
        try:
            installed_count = install_target(args.target, inventory, args.codex_home, args.opencode_home, args.dry_run)
        except ValueError as exc:
            print(f"Compatibility install failed for target '{args.target}'.", file=sys.stderr)
            print(f"- {exc}", file=sys.stderr)
            return 1
        action = "Would install" if args.dry_run else "Installed"
        print(f"{action} {installed_count} {target_display_name(args.target)} agents into {target_home(args.target, args.codex_home, args.opencode_home)}.")
        return 0

    print(f"Compatibility check passed for target '{args.target}'.")
    print(f"Agents: {len(inventory.agents)}")
    print(f"Skills: {len(inventory.skills)}")
    return 0


def check_target_supported(target: str, path: Path) -> tuple[ValidationMessage, ...]:
    if target in SUPPORTED_TARGETS:
        return ()
    return (ValidationMessage(path, f"unsupported compatibility target: {target}"),)


def validate_target(target: str, inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    if target == CODEX_TARGET:
        return validate_codex(inventory)
    if target == OPENCODE_TARGET:
        return validate_opencode(inventory)
    return (ValidationMessage(inventory.root, f"unsupported compatibility target: {target}"),)


def install_target(
    target: str,
    inventory: AssetInventory,
    codex_home: Path,
    opencode_home: Path,
    dry_run: bool,
) -> int:
    if target == CODEX_TARGET:
        return install_codex_agents(
            inventory,
            codex_home=codex_home.expanduser().resolve(),
            dry_run=dry_run,
        )
    if target == OPENCODE_TARGET:
        return install_opencode_assets(
            inventory,
            opencode_home=opencode_home.expanduser().resolve(),
            dry_run=dry_run,
        )
    raise ValueError(f"unsupported compatibility target: {target}")


def target_home(target: str, codex_home: Path, opencode_home: Path) -> Path:
    if target == OPENCODE_TARGET:
        return opencode_home.expanduser().resolve()
    return codex_home.expanduser().resolve()


def target_display_name(target: str) -> str:
    if target == OPENCODE_TARGET:
        return "OpenCode"
    return "Codex"


if __name__ == "__main__":
    raise SystemExit(main())
