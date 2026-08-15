#!/usr/bin/env python3
"""Repository-wide surface checks that the state.yml validator does not cover.

The catalog itself (which skills, subagents, rules, MCP servers, and hooks exist, and
whether they match the files on disk) is owned by `mires validate`. This script adds the
repository-level checks: broken inline path references, stale legacy runtime names, and a
smoke test of every supported compatibility target.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from mires.state import load_state, state_path, validate_state
from mires.state.models import SECTIONS

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src" / "mires"
ARCHIVED_CHANGES = ROOT / "openspec" / "changes" / "archive"
CHANGE_WORKSPACE = ROOT / "openspec" / "changes"
HANDBOOKS = tuple(ROOT.glob("skills/*/references/handbook"))

IGNORED_PARTS = {".git", ".tmp", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache"}
LOCAL_RUNTIME_PARTS = {".codex", ".opencode"}
SCANNED_SUFFIXES = {"", ".md", ".yaml", ".yml", ".py", ".js", ".json", ".toml", ".sh"}
# Inline path references are a documentation convention; source files contain regex
# literals and string fragments that only look like paths.
DOCUMENTED_SUFFIXES = {".md", ".yaml", ".yml"}

# Only catalog paths are checked. A `src/...` reference inside a skill describes the
# target project being worked on, not this repository.
CATALOG_PREFIXES = tuple(section.directory for section in SECTIONS)
REFERENCE_PATTERN = re.compile(rf"`((?:{'|'.join(CATALOG_PREFIXES)})/[^`]+)`")

LEGACY_GRANULAR_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"\bmacwdo-(?:agent|backend|explorer|planner|project|python|react|researcher|reviewer|tester|typescript)\b",
        r"\bmires-(?:agent-testing|backend-orchestrator|python-|react-query|react-hook-form|typescript-|zod)\b",
        r"\bopenspec-(?:apply-change|archive-change|explore|propose)\b",
        r"\.codex/skills",
        r"\.ai/(?:agents|skills)",
    ]
]

FORBIDDEN_RUNTIME_TREES = (ROOT / ".codex", ROOT / ".opencode")

COMPATIBILITY_FILES = (
    SRC / "cli.py",
    SRC / "compatibility" / "__init__.py",
    SRC / "compatibility" / "models.py",
    SRC / "compatibility" / "parsing.py",
    SRC / "compatibility" / "codex.py",
    SRC / "compatibility" / "opencode.py",
    SRC / "state" / "models.py",
    SRC / "state" / "loader.py",
    SRC / "state" / "validate.py",
)


class VerificationError(Exception):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def relative(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def is_ignored(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    if any(part in IGNORED_PARTS or part in LOCAL_RUNTIME_PARTS for part in parts):
        return True
    return ARCHIVED_CHANGES in path.parents or CHANGE_WORKSPACE in path.parents


def active_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix in SCANNED_SUFFIXES and not is_ignored(path)
    ]


def check_catalog() -> None:
    """Delegate every catalog question to the state.yml validator."""
    state = load_state(ROOT)
    errors = validate_state(ROOT, state)
    if errors:
        details = "\n".join(f"  - {error.format(ROOT)}" for error in errors)
        fail(f"catalog validation failed:\n{details}")
    if not state.config.profiles:
        fail(f"{relative(state_path(ROOT))}: at least one profile must be defined")


def check_references_exist(files: list[Path]) -> None:
    """Every inline `catalog/path` written in backticks must resolve to a real file."""
    for path in files:
        if path.suffix not in DOCUMENTED_SUFFIXES:
            continue
        if any(handbook in path.parents for handbook in HANDBOOKS):
            continue
        for match in REFERENCE_PATTERN.findall(path.read_text()):
            if any(token in match for token in ("<", ">", "*")):
                continue
            if not (ROOT / match).exists():
                fail(f"broken referenced path in {relative(path)}: {match}")


def check_no_legacy_granular_surfaces(files: list[Path]) -> None:
    for path in files:
        # This file spells out the legacy names it looks for.
        if path == Path(__file__).resolve():
            continue
        text = path.read_text()
        for pattern in LEGACY_GRANULAR_PATTERNS:
            match = pattern.search(text)
            if match:
                fail(f"stale legacy runtime reference in {relative(path)}: {match.group(0)}")
        if path.name == "SKILL.md" and re.search(r"compatibility\s+redirect", text, re.IGNORECASE):
            fail(f"active compatibility redirect skill package: {relative(path)}")


def check_no_duplicate_runtime_trees() -> None:
    for path in FORBIDDEN_RUNTIME_TREES:
        if path.exists() and tracked_files_under(path):
            fail(f"duplicate runtime tree is active: {relative(path)}")


def tracked_files_under(path: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", str(relative(path))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip() and (ROOT / line).exists()]


def check_compatibility_tooling() -> None:
    for path in COMPATIBILITY_FILES:
        if not path.exists():
            fail(f"missing compatibility tooling file: {relative(path)}")

    for target in ("codex", "opencode"):
        result = run_cli("--target", target)
        if result.returncode != 0:
            fail(f"{target} compatibility check failed: {result.stderr.strip() or result.stdout.strip()}")

    unsupported = run_cli("--target", "unsupported-runtime")
    if unsupported.returncode == 0:
        fail("unsupported compatibility target unexpectedly succeeded")
    if "unsupported compatibility target" not in unsupported.stderr:
        fail("unsupported compatibility target did not report a clear error")


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mires.cli", "--root", str(ROOT), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    files = active_files()
    try:
        check_catalog()
        check_no_duplicate_runtime_trees()
        check_references_exist(files)
        check_no_legacy_granular_surfaces(files)
        check_compatibility_tooling()
    except VerificationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Mires surface verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
