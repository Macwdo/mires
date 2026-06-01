#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from compatibility.codex import SUPPORTED_TARGET, check_target_supported, validate_codex
from compatibility.parsing import load_inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate runtime compatibility for canonical Mires .ai assets."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=["check"],
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
        print(f"Compatibility check failed for target '{args.target}'.", file=sys.stderr)
        for error in errors:
            print(f"- {error.format(root)}", file=sys.stderr)
        return 1

    print(f"Compatibility check passed for target '{args.target}'.")
    print(f"Agents: {len(inventory.agents)}")
    print(f"Skills: {len(inventory.skills)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
