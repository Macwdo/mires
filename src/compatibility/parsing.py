from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from compatibility.models import AgentAsset, AssetInventory, SkillAsset, ValidationMessage


AI_DIR = ".ai"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
AGENT_FILE = "AGENT.md"
SKILL_FILE = "SKILL.md"
OPENAI_METADATA = "openai.yaml"


class FrontMatterError(ValueError):
    pass


def load_inventory(root: Path) -> AssetInventory:
    root = root.resolve()
    errors: list[ValidationMessage] = []
    agents = _load_agents(root, errors)
    skills = _load_skills(root, errors)
    return AssetInventory(
        root=root,
        agents=tuple(agents),
        skills=tuple(skills),
        errors=tuple(errors),
    )


def _load_agents(root: Path, errors: list[ValidationMessage]) -> list[AgentAsset]:
    agents_root = root / AI_DIR / AGENTS_DIR
    if not agents_root.exists():
        errors.append(ValidationMessage(agents_root, "missing canonical agents directory"))
        return []

    agents: list[AgentAsset] = []
    for path in sorted(agents_root.glob(f"*/{AGENT_FILE}")):
        try:
            frontmatter = read_frontmatter(path)
        except FrontMatterError as exc:
            errors.append(ValidationMessage(path, str(exc)))
            continue

        name = _required_string(frontmatter, "name", path, errors)
        description = _required_string(frontmatter, "description", path, errors)
        parent = _optional_string(frontmatter, "parent")
        children = _string_tuple(frontmatter.get("children"), path, "children", errors)
        metadata_path = path.parent / AGENTS_DIR / OPENAI_METADATA
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            try:
                metadata = read_simple_yaml(metadata_path)
            except FrontMatterError as exc:
                errors.append(ValidationMessage(metadata_path, str(exc)))
        else:
            errors.append(ValidationMessage(metadata_path, "missing Codex/OpenAI runtime metadata"))

        if name and description:
            agents.append(
                AgentAsset(
                    name=name,
                    description=description,
                    parent=parent,
                    children=children,
                    path=path,
                    metadata_path=metadata_path if metadata_path.exists() else None,
                    metadata=metadata,
                )
            )
    return agents


def _load_skills(root: Path, errors: list[ValidationMessage]) -> list[SkillAsset]:
    skills_root = root / AI_DIR / SKILLS_DIR
    if not skills_root.exists():
        errors.append(ValidationMessage(skills_root, "missing canonical skills directory"))
        return []

    skills: list[SkillAsset] = []
    for path in sorted(skills_root.glob(f"*/{SKILL_FILE}")):
        try:
            frontmatter = read_frontmatter(path)
        except FrontMatterError as exc:
            errors.append(ValidationMessage(path, str(exc)))
            continue

        name = _required_string(frontmatter, "name", path, errors)
        description = _required_string(frontmatter, "description", path, errors)
        reference_paths = _declared_reference_paths(path)
        for reference_path in reference_paths:
            if not reference_path.exists():
                errors.append(ValidationMessage(reference_path, "declared reference path does not exist"))

        if name and description:
            skills.append(
                SkillAsset(
                    name=name,
                    description=description,
                    path=path,
                    reference_paths=tuple(reference_paths),
                )
            )
    return skills


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise FrontMatterError("missing YAML front matter")
    end = text.find("\n---", 4)
    if end == -1:
        raise FrontMatterError("unterminated YAML front matter")
    return parse_simple_yaml(text[4:end])


def read_simple_yaml(path: Path) -> dict[str, Any]:
    return parse_simple_yaml(path.read_text())


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any], str | None]] = [(-1, root, None)]

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise FrontMatterError(f"invalid indentation near: {line}")
        current = stack[-1][1]
        pending_key = stack[-1][2]

        if line.startswith("- "):
            if pending_key is None:
                raise FrontMatterError(f"list item without key near: {line}")
            existing = current.get(pending_key)
            if existing is None:
                existing = []
                current[pending_key] = existing
            if not isinstance(existing, list):
                raise FrontMatterError(f"mixed scalar and list value for: {pending_key}")
            existing.append(_parse_scalar(line[2:].strip()))
            continue

        if pending_key is not None and current.get(pending_key) is None:
            child = {}
            current[pending_key] = child
            stack[-1] = (stack[-1][0], child, None)
            current = child

        if ":" not in line:
            raise FrontMatterError(f"expected key/value near: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise FrontMatterError(f"empty key near: {line}")
        if raw_value == "":
            current[key] = None
            stack.append((indent, current, key))
        else:
            current[key] = _parse_scalar(raw_value)
            stack[-1] = (stack[-1][0], current, key)

    return root


def _parse_scalar(value: str) -> Any:
    if value in {"[]", "[ ]"}:
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _required_string(
    data: dict[str, Any],
    key: str,
    path: Path,
    errors: list[ValidationMessage],
) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    errors.append(ValidationMessage(path, f"missing required string front matter field: {key}"))
    return ""


def _optional_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    return value.strip() if isinstance(value, str) else ""


def _string_tuple(
    value: Any,
    path: Path,
    key: str,
    errors: list[ValidationMessage],
) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(item.strip() for item in value if item.strip())
    errors.append(ValidationMessage(path, f"field must be a list of strings: {key}"))
    return ()


def _declared_reference_paths(skill_path: Path) -> list[Path]:
    text = skill_path.read_text()
    references: set[Path] = set()
    for match in re.findall(r"`(references/[^`]+\.md)`", text):
        references.add(skill_path.parent / match)
    return sorted(references)
