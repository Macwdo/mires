#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mires.compatibility.codex import SUPPORTED_TARGET as CODEX_TARGET
from mires.compatibility.codex import install_codex_agents, validate_codex
from mires.compatibility.models import AssetInventory, ValidationMessage
from mires.compatibility.opencode import SUPPORTED_TARGET as OPENCODE_TARGET
from mires.compatibility.opencode import install_opencode_assets, validate_opencode
from mires.compatibility.parsing import filter_inventory, load_inventory
from mires.state import MiresState, StateFileError, load_state, validate_state

SUPPORTED_TARGETS = (CODEX_TARGET, OPENCODE_TARGET)

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_UNSUPPORTED = 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        state = load_state(root)
    except StateFileError as exc:
        return report(f"Failed to load {exc.path.name}.", exc.messages, root)

    state_errors = validate_state(root, state)
    if state_errors:
        return report("Catalog validation failed.", state_errors, root)

    if args.command == "validate":
        print_state_summary(state)
        return EXIT_OK

    if args.target not in SUPPORTED_TARGETS:
        print(f"unsupported compatibility target: {args.target}", file=sys.stderr)
        return EXIT_UNSUPPORTED

    try:
        inventory = select_inventory(root, state, args.profile)
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INVALID

    target_errors = validate_target(args.target, inventory)
    if target_errors:
        return report(f"Compatibility {args.command} failed for target '{args.target}'.", target_errors, root)

    if args.command == "install":
        return run_install(args, inventory)

    print(f"Compatibility check passed for target '{args.target}'.")
    print(f"Agents: {len(inventory.agents)}")
    print(f"Skills: {len(inventory.skills)}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the Mires catalog and install it into a supported runtime.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=["validate", "check", "install"],
        help="validate the catalog, check runtime compatibility, or install into a runtime.",
    )
    parser.add_argument(
        "--target",
        default=CODEX_TARGET,
        help=f"Runtime target. Supported: {', '.join(SUPPORTED_TARGETS)}.",
    )
    parser.add_argument(
        "--profile",
        help="Install or check only the assets a state.yml profile selects. Defaults to the whole catalog.",
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
    return parser


def select_inventory(root: Path, state: MiresState, profile_slug: str | None) -> AssetInventory:
    inventory = load_inventory(root)
    if profile_slug is None:
        return inventory
    profile = state.profile(profile_slug)
    if profile is None:
        known = ", ".join(state.profile_slugs()) or "none"
        raise LookupError(f"unknown profile: {profile_slug}. Known profiles: {known}")
    return filter_inventory(inventory, set(profile.using.subagents), set(profile.using.skills))


def run_install(args: argparse.Namespace, inventory: AssetInventory) -> int:
    try:
        installed = install_target(args.target, inventory, args.codex_home, args.opencode_home, args.dry_run)
    except ValueError as exc:
        print(f"Compatibility install failed for target '{args.target}'.", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return EXIT_INVALID
    action = "Would install" if args.dry_run else "Installed"
    home = target_home(args.target, args.codex_home, args.opencode_home)
    print(f"{action} {installed} {target_display_name(args.target)} agents into {home}.")
    return EXIT_OK


def validate_target(target: str, inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    if target == CODEX_TARGET:
        return validate_codex(inventory)
    return validate_opencode(inventory)


def install_target(
    target: str,
    inventory: AssetInventory,
    codex_home: Path,
    opencode_home: Path,
    dry_run: bool,
) -> int:
    if target == CODEX_TARGET:
        return install_codex_agents(inventory, codex_home=codex_home.expanduser().resolve(), dry_run=dry_run)
    return install_opencode_assets(inventory, opencode_home=opencode_home.expanduser().resolve(), dry_run=dry_run)


def target_home(target: str, codex_home: Path, opencode_home: Path) -> Path:
    home = opencode_home if target == OPENCODE_TARGET else codex_home
    return home.expanduser().resolve()


def target_display_name(target: str) -> str:
    return "OpenCode" if target == OPENCODE_TARGET else "Codex"


def print_state_summary(state: MiresState) -> None:
    print("Catalog validation passed.")
    print(
        f"Profiles: {len(state.config.profiles)} "
        f"({', '.join(state.profile_slugs()) if state.config.profiles else 'none'})"
    )
    for field in ("mcps", "skills", "subagents", "rules", "hooks"):
        print(f"{field.capitalize()}: {len(state.entries(field))}")


def report(headline: str, messages: tuple[ValidationMessage, ...], root: Path) -> int:
    print(headline, file=sys.stderr)
    for message in messages:
        print(f"- {message.format(root)}", file=sys.stderr)
    return EXIT_INVALID


if __name__ == "__main__":
    raise SystemExit(main())
