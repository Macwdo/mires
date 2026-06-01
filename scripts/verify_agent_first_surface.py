#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / ".ai"
AI_AGENTS = AI / "agents"
AI_SKILLS = AI / "skills"
ARCHIVED_CHANGES = ROOT / "openspec" / "changes" / "archive"
CHANGE_WORKSPACE = ROOT / "openspec" / "changes"
SRC = ROOT / "src"
IGNORED_ACTIVE_PARTS = {".git", ".tmp", "__pycache__"}

AGENTS = {
    "orchestrator": {
        "children": {"explorer", "backend", "frontend", "tester", "reviewer", "planner", "researcher"},
    },
    "explorer": {"children": set()},
    "backend": {"children": set()},
    "frontend": {"children": set()},
    "tester": {"children": set()},
    "reviewer": {"children": set()},
    "planner": {"children": set()},
    "researcher": {"children": set()},
}

SKILLS = {
    "backend",
    "python",
    "django",
    "fastapi",
    "sqlalchemy",
    "postgres",
    "celery",
    "frontend",
    "react",
    "next",
    "typescript",
    "testing",
    "review",
    "project-conventions",
    "openspec",
    "langgraph",
}

LEGACY_GRANULAR_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"\bmacwdo-(?:agent|backend|explorer|planner|project|python|react|researcher|reviewer|tester|typescript)\b",
        r"\bmires-(?:agent-testing|backend-orchestrator|python-|react-query|react-hook-form|typescript-|zod)\b",
        r"\bopenspec-(?:apply-change|archive-change|explore|propose)\b",
        r"\.codex/skills",
        r"\.opencode",
        r"\bOpenCode\b",
        r"\bopencode\b",
    ]
]

ALLOWED_STALE_ACTIVE_PATHS = {
    Path("MIGRATION.md"),
    Path("scripts/verify_agent_first_surface.py"),
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*([^\n]+)$", text, re.MULTILINE)
    return match.group(1).strip().strip('"') if match else None


def read_children(frontmatter: str) -> set[str]:
    raw = frontmatter_value(frontmatter, "children")
    if raw is None:
        return set()
    stripped = raw.strip()
    if stripped in {"", "[]"}:
        return set()
    if not stripped.startswith("[") or not stripped.endswith("]"):
        fail(f"children must be inline list: {stripped}")
    return {item.strip() for item in stripped[1:-1].split(",") if item.strip()}


def assert_contains(text: str, needle: str, path: Path) -> None:
    if needle not in text:
        fail(f"missing required text in {path.relative_to(ROOT)}: {needle}")


def is_ignored_path(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True
    if any(part in IGNORED_ACTIVE_PARTS for part in relative.parts):
        return True
    if ARCHIVED_CHANGES in path.parents:
        return True
    if CHANGE_WORKSPACE in path.parents:
        return True
    return False


def active_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if is_ignored_path(path):
            continue
        if path.is_file() and path.suffix in {"", ".md", ".yaml", ".yml", ".py", ".js", ".json", ".toml", ".sh"}:
            files.append(path)
    return files


def validate_agent(name: str, expected_children: set[str]) -> None:
    agent_dir = AI_AGENTS / name
    agent_path = agent_dir / "AGENT.md"
    metadata_path = agent_dir / "agents" / "openai.yaml"
    text = read(agent_path)
    metadata = read(metadata_path)
    if frontmatter_value(text, "name") != name:
        fail(f"front matter name mismatch in {agent_path.relative_to(ROOT)}")
    if f'name: "{name}"' not in metadata and f'display_name: "{name}"' not in metadata:
        fail(f"runtime metadata does not preserve name: {metadata_path.relative_to(ROOT)}")
    children = read_children(text)
    if children != expected_children:
        fail(f"child list mismatch in {agent_path.relative_to(ROOT)}: expected {sorted(expected_children)}, got {sorted(children)}")


def validate_skill(name: str) -> None:
    skill_dir = AI_SKILLS / name
    skill_path = skill_dir / "SKILL.md"
    references_dir = skill_dir / "references"
    text = read(skill_path)
    if frontmatter_value(text, "name") != name:
        fail(f"front matter name mismatch in {skill_path.relative_to(ROOT)}")
    for section in [
        "## When To Use",
        "## Core Rules",
        "## Preferred Patterns",
        "## Anti-Patterns",
        "## Checklist",
        "## References Index",
    ]:
        assert_contains(text, section, skill_path)
    if not references_dir.exists():
        fail(f"missing references directory: {references_dir.relative_to(ROOT)}")
    reference_files = sorted(references_dir.glob("*.md"))
    for reference in reference_files:
        rel_reference = f"references/{reference.name}"
        if rel_reference not in text:
            fail(f"reference is not documented by owner {skill_path.relative_to(ROOT)}: {rel_reference}")


def check_references_exist(base: Path) -> None:
    files = [base] if base.is_file() else list(base.rglob("*"))
    for path in files:
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml", ".py"}:
            continue
        text = read(path)
        for match in re.findall(r"`((?:\.ai|scripts)/[^`]+)`", text):
            if any(token in match for token in ["<", ">", "*"]):
                continue
            target = ROOT / match
            if not target.exists():
                fail(f"broken referenced path in {path.relative_to(ROOT)}: {match}")


def check_no_duplicate_runtime_trees() -> None:
    forbidden_dirs = {
        ROOT / ".codex",
        ROOT / ".opencode",
    }
    for path in forbidden_dirs:
        if path.exists():
            fail(f"duplicate runtime tree is active: {path.relative_to(ROOT)}")


def check_no_legacy_granular_surfaces() -> None:
    for path in active_files():
        relative = path.relative_to(ROOT)
        if relative in ALLOWED_STALE_ACTIVE_PATHS:
            continue
        text = read(path)
        for pattern in LEGACY_GRANULAR_PATTERNS:
            match = pattern.search(text)
            if match:
                fail(f"stale legacy runtime reference in {relative}: {match.group(0)}")
        if path.name == "SKILL.md" and re.search(r"compatibility\s+redirect", text, re.IGNORECASE):
            fail(f"active compatibility redirect skill package: {relative}")


def check_compatibility_tooling() -> None:
    for path in [
        SRC / "main.py",
        SRC / "compatibility" / "__init__.py",
        SRC / "compatibility" / "models.py",
        SRC / "compatibility" / "parsing.py",
        SRC / "compatibility" / "codex.py",
    ]:
        if not path.exists():
            fail(f"missing compatibility tooling file: {path.relative_to(ROOT)}")

    result = subprocess.run(
        [sys.executable, str(SRC / "main.py"), "--target", "codex", "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Codex compatibility check failed: {result.stderr.strip() or result.stdout.strip()}")

    unsupported_result = subprocess.run(
        [sys.executable, str(SRC / "main.py"), "--target", "unsupported-runtime", "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if unsupported_result.returncode == 0:
        fail("unsupported compatibility target unexpectedly succeeded")
    if "unsupported compatibility target" not in unsupported_result.stderr:
        fail("unsupported compatibility target did not report a clear error")


assert_contains(read(AI / "AGENTS.md"), "orchestrator", AI / "AGENTS.md")
assert_contains(read(AI / "AGENTS.md"), "Only one final implementation agent should edit files.", AI / "AGENTS.md")

for agent_name, config in AGENTS.items():
    validate_agent(agent_name, config["children"])

assert_contains(read(AI_AGENTS / "orchestrator" / "AGENT.md"), "Only one final implementation agent should modify files.", AI_AGENTS / "orchestrator" / "AGENT.md")
assert_contains(read(AI_AGENTS / "backend" / "AGENT.md"), "skills/backend", AI_AGENTS / "backend" / "AGENT.md")
assert_contains(read(AI_AGENTS / "frontend" / "AGENT.md"), "skills/frontend", AI_AGENTS / "frontend" / "AGENT.md")
assert_contains(read(AI_AGENTS / "explorer" / "AGENT.md"), "Do not modify files.", AI_AGENTS / "explorer" / "AGENT.md")
assert_contains(read(AI_AGENTS / "tester" / "AGENT.md"), "skills/testing", AI_AGENTS / "tester" / "AGENT.md")
assert_contains(read(AI_AGENTS / "reviewer" / "AGENT.md"), "Do not modify files unless explicitly requested.", AI_AGENTS / "reviewer" / "AGENT.md")
researcher_text = read(AI_AGENTS / "researcher" / "AGENT.md")
assert_contains(researcher_text, "official docs", AI_AGENTS / "researcher" / "AGENT.md")
assert_contains(researcher_text, "source repositories", AI_AGENTS / "researcher" / "AGENT.md")
assert_contains(researcher_text, "discovered facts from recommendations", AI_AGENTS / "researcher" / "AGENT.md")

actual_agent_dirs = {path.name for path in AI_AGENTS.iterdir() if path.is_dir()}
if actual_agent_dirs != set(AGENTS):
    fail(f"unexpected agent directories: {sorted(actual_agent_dirs)}")

actual_skill_dirs = {path.name for path in AI_SKILLS.iterdir() if path.is_dir()}
if actual_skill_dirs != SKILLS:
    fail(f"unexpected skill directories: {sorted(actual_skill_dirs)}")

check_no_duplicate_runtime_trees()
check_no_legacy_granular_surfaces()
check_compatibility_tooling()

for skill_name in SKILLS:
    validate_skill(skill_name)

check_references_exist(AI)
check_references_exist(ROOT / "AGENTS.md")

print("Agent-first .ai surface verification passed.")
