#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mires.catalog import CatalogNotFoundError, resolve_root
from mires.compatibility.models import AssetInventory, InstallReport, ValidationMessage
from mires.compatibility.parsing import filter_inventory, load_inventory
from mires.compatibility.targets import ALL_TARGETS, TARGET_SLUGS, TARGETS, Target, resolve_targets
from mires.project.cli import main as project_main
from mires.state import MiresState, StateFileError, load_state, validate_state

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_UNSUPPORTED = 2

DEFAULT_TARGET = ALL_TARGETS

# Projects are synced, not installed, so they get their own command group rather than
# another flag on a command whose every option is about runtime homes.
PROJECT_COMMAND = "project"
PROJECT_SYNC_ALIAS = "project-sync"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (PROJECT_COMMAND, PROJECT_SYNC_ALIAS):
        rest = argv[1:] if argv[0] == PROJECT_COMMAND else ["sync", *argv[1:]]
        return project_main(rest)

    args = build_parser().parse_args(argv)

    try:
        root = resolve_root(args.root)
    except CatalogNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INVALID

    try:
        state = load_state(root)
    except StateFileError as exc:
        return report(f"Failed to load {exc.path.name}.", exc.messages, root)

    state_errors = validate_state(root, state)
    if state_errors:
        return report("Catalog validation failed.", state_errors, root)

    if args.command == "validate":
        print_state_summary(root, state)
        return EXIT_OK

    try:
        targets = resolve_targets(args.target)
        inventory = select_inventory(root, state, args.profile)
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_UNSUPPORTED if "target" in str(exc) else EXIT_INVALID

    exit_code = EXIT_OK
    for target in targets:
        target_errors = target.validate(inventory)
        if target_errors:
            report(f"Compatibility {args.command} failed for target '{target.slug}'.", target_errors, root)
            exit_code = EXIT_INVALID
            continue
        if args.command == "install":
            exit_code = run_install(target, inventory, args) or exit_code
        else:
            print(f"Compatibility check passed for target '{target.slug}'.")
            print_inventory_summary(inventory)
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mires",
        description="Validate the Mires catalog and install it into every supported agent runtime.",
        epilog=(
            f"`mires {PROJECT_COMMAND} <action>` syncs a single project with a git repository "
            f"instead of installing the catalog. `mires {PROJECT_SYNC_ALIAS}` is short for "
            f"`mires {PROJECT_COMMAND} sync`. Run `mires {PROJECT_COMMAND} --help` for its options."
        ),
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
        default=DEFAULT_TARGET,
        help=f"Runtime target. Supported: {', '.join((*TARGET_SLUGS, ALL_TARGETS))}. Defaults to {ALL_TARGETS}.",
    )
    parser.add_argument(
        "--profile",
        help="Install or check only the assets a state.yml profile selects. Defaults to the whole catalog.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Catalog root. Defaults to the nearest state.yml, then the catalog bundled in the package.",
    )
    for target in TARGETS.values():
        parser.add_argument(
            target.destination,
            type=Path,
            help=f"{target.display_name} home directory. Defaults to {target.default_home()}.",
        )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview install output without writing files.",
    )
    return parser


def select_inventory(root: Path, state: MiresState, profile_slug: str | None) -> AssetInventory:
    inventory = load_inventory(root, state)
    if profile_slug is None:
        return inventory
    profile = state.profile(profile_slug)
    if profile is None:
        known = ", ".join(state.profile_slugs()) or "none"
        raise LookupError(f"unknown profile: {profile_slug}. Known profiles: {known}")
    return filter_inventory(
        inventory,
        set(profile.using.subagents),
        set(profile.using.skills),
        set(profile.using.rules),
        set(profile.using.mcps),
        set(profile.using.hooks),
    )


def run_install(target: Target, inventory: AssetInventory, args: argparse.Namespace) -> int:
    home = target_home(target, args)
    try:
        installed = target.install(inventory, home, args.dry_run)
    except ValueError as exc:
        print(f"Compatibility install failed for target '{target.slug}'.", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return EXIT_INVALID
    print_install_report(target, installed, args.dry_run)
    return EXIT_OK


def target_home(target: Target, args: argparse.Namespace) -> Path:
    override = getattr(args, target.option, None)
    home = override if override is not None else target.default_home()
    return home.expanduser().resolve()


def print_install_report(target: Target, installed: InstallReport, dry_run: bool) -> None:
    action = "Would install" if dry_run else "Installed"
    print(f"{action} {installed.summary()} for {target.display_name} into {installed.home}.")
    if installed.unsupported:
        kinds = ", ".join(installed.unsupported)
        print(f"  {target.display_name} has no runtime for: {kinds}. Skipped.")


def print_inventory_summary(inventory: AssetInventory) -> None:
    print(f"Subagents: {len(inventory.agents)}")
    print(f"Skills: {len(inventory.skills)}")
    print(f"Rules: {len(inventory.rules)}")
    print(f"Mcps: {len(inventory.mcps)}")
    print(f"Hooks: {len(inventory.hooks)}")


def print_state_summary(root: Path, state: MiresState) -> None:
    print("Catalog validation passed.")
    print(f"Root: {root}")
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
