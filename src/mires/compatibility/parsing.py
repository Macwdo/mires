from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from mires.compatibility.models import AgentAsset, AssetInventory, SkillAsset, ValidationMessage
from mires.frontmatter import FrontMatterError, read_frontmatter, read_yaml_mapping

__all__ = ["FrontMatterError", "filter_inventory", "load_inventory", "read_frontmatter"]

SUBAGENTS_DIR = "subagents"
SKILLS_DIR = "skills"
AGENT_METADATA_DIR = "agents"
AGENT_FILE = "AGENT.md"
SKILL_FILE = "SKILL.md"
OPENAI_METADATA = "openai.yaml"


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


def filter_inventory(
    inventory: AssetInventory,
    agent_names: set[str],
    skill_names: set[str],
) -> AssetInventory:
    """Narrow an inventory to the assets a profile selects."""
    return AssetInventory(
        root=inventory.root,
        agents=tuple(agent for agent in inventory.agents if agent.name in agent_names),
        skills=tuple(skill for skill in inventory.skills if skill.name in skill_names),
        errors=inventory.errors,
    )


def _load_agents(root: Path, errors: list[ValidationMessage]) -> list[AgentAsset]:
    agents_root = root / SUBAGENTS_DIR
    if not agents_root.exists():
        errors.append(ValidationMessage(agents_root, "missing canonical subagents directory"))
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
        metadata_path = path.parent / AGENT_METADATA_DIR / OPENAI_METADATA
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            try:
                metadata = read_yaml_mapping(metadata_path)
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
    skills_root = root / SKILLS_DIR
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
