#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from compatibility.codex import SUPPORTED_TARGET, check_target_supported, install_codex_agents, validate_codex
from compatibility.parsing import load_inventory


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
        default=SUPPORTED_TARGET,
        help=f"Runtime target to validate. Supported: {SUPPORTED_TARGET}.",
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
    errors = validate_codex(inventory)
    if errors:
        print(f"Compatibility {args.command} failed for target '{args.target}'.", file=sys.stderr)
        for error in errors:
            print(f"- {error.format(root)}", file=sys.stderr)
        return 1

    if args.command == "install":
        try:
            installed_count = install_codex_agents(
                inventory,
                codex_home=args.codex_home.expanduser().resolve(),
                dry_run=args.dry_run,
            )
        except ValueError as exc:
            print(f"Compatibility install failed for target '{args.target}'.", file=sys.stderr)
            print(f"- {exc}", file=sys.stderr)
            return 1
        action = "Would install" if args.dry_run else "Installed"
        print(f"{action} {installed_count} Codex agents into {args.codex_home.expanduser().resolve()}.")
        return 0

    print(f"Compatibility check passed for target '{args.target}'.")
    print(f"Agents: {len(inventory.agents)}")
    print(f"Skills: {len(inventory.skills)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
