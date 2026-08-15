from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mires.compatibility.models import (
    AgentAsset,
    AssetInventory,
    HookAsset,
    McpAsset,
    RuleAsset,
    SkillAsset,
    ValidationMessage,
)
from mires.frontmatter import FrontMatterError, read_frontmatter, read_yaml_mapping
from mires.state import MiresState

__all__ = ["FrontMatterError", "filter_inventory", "load_inventory", "read_frontmatter"]

SUBAGENTS_DIR = "subagents"
SKILLS_DIR = "skills"
RULES_DIR = "rules"
MCPS_DIR = "mcps"
HOOKS_DIR = "hooks"
SPECS_DIR = "openspec/specs"
AGENT_METADATA_DIR = "agents"
AGENT_FILE = "AGENT.md"
SKILL_FILE = "SKILL.md"
MCP_FILE = "mcp.json"
HOOKS_FILE = "hooks.json"
OPENAI_METADATA = "openai.yaml"

# The canonical event vocabulary a hooks.json may bind to. Each target maps these
# onto its own runtime event names, and drops the ones it cannot express.
CANONICAL_HOOK_EVENTS = (
    "beforeSubmitPrompt",
    "beforeShellExecution",
    "beforeReadFile",
    "afterFileEdit",
    "stop",
)


def load_inventory(root: Path, state: MiresState) -> AssetInventory:
    root = root.resolve()
    errors: list[ValidationMessage] = []
    return AssetInventory(
        root=root,
        agents=tuple(_load_agents(root, errors)),
        skills=tuple(_load_skills(root, errors)),
        rules=tuple(_load_rules(root, state, errors)),
        mcps=tuple(_load_mcps(root, state, errors)),
        hooks=tuple(_load_hooks(root, state, errors)),
        specs=tuple(_load_specs(root)),
        errors=tuple(errors),
    )


def filter_inventory(
    inventory: AssetInventory,
    agent_names: set[str],
    skill_names: set[str],
    rule_names: set[str] | None = None,
    mcp_names: set[str] | None = None,
    hook_names: set[str] | None = None,
) -> AssetInventory:
    """Narrow an inventory to the assets a profile selects."""
    return AssetInventory(
        root=inventory.root,
        agents=tuple(agent for agent in inventory.agents if agent.name in agent_names),
        skills=tuple(skill for skill in inventory.skills if skill.name in skill_names),
        rules=tuple(rule for rule in inventory.rules if _selected(rule.name, rule_names)),
        mcps=tuple(mcp for mcp in inventory.mcps if _selected(mcp.name, mcp_names)),
        hooks=tuple(hook for hook in inventory.hooks if _selected(hook.name, hook_names)),
        specs=inventory.specs,
        errors=inventory.errors,
    )


def _selected(name: str, selection: set[str] | None) -> bool:
    return True if selection is None else name in selection


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


def _load_rules(root: Path, state: MiresState, errors: list[ValidationMessage]) -> list[RuleAsset]:
    rules: list[RuleAsset] = []
    for entry in state.rules:
        path = root / state.entry_path("rules", entry)
        if not path.exists():
            errors.append(ValidationMessage(path, "declared rule file does not exist"))
            continue
        rules.append(RuleAsset(name=entry.slug, description=entry.description, path=path))
    return rules


def _load_mcps(root: Path, state: MiresState, errors: list[ValidationMessage]) -> list[McpAsset]:
    mcps: list[McpAsset] = []
    for entry in state.mcps:
        path = root / state.entry_path("mcps", entry) / MCP_FILE
        document = _read_json_mapping(path, errors)
        if document is None:
            continue

        declared_name = document.get("name")
        if declared_name is not None and declared_name != entry.slug:
            errors.append(ValidationMessage(path, f"name must match the declared slug: {entry.slug}"))
        server = {key: value for key, value in document.items() if key != "name"}
        if not server.get("command") and not server.get("url"):
            errors.append(ValidationMessage(path, "server must declare either `command` or `url`"))
            continue

        mcps.append(McpAsset(name=entry.slug, description=entry.description, path=path, server=server))
    return mcps


def _load_hooks(root: Path, state: MiresState, errors: list[ValidationMessage]) -> list[HookAsset]:
    hooks: list[HookAsset] = []
    for entry in state.hooks:
        path = root / state.entry_path("hooks", entry) / HOOKS_FILE
        document = _read_json_mapping(path, errors)
        if document is None:
            continue

        declared = document.get("hooks")
        if not isinstance(declared, dict) or not declared:
            errors.append(ValidationMessage(path, "hooks must be a non-empty mapping of event to commands"))
            continue

        events: dict[str, tuple[dict[str, Any], ...]] = {}
        for event, commands in declared.items():
            if event not in CANONICAL_HOOK_EVENTS:
                known = ", ".join(CANONICAL_HOOK_EVENTS)
                errors.append(ValidationMessage(path, f"unknown hook event: {event}. Known events: {known}"))
                continue
            if not isinstance(commands, list) or not all(isinstance(item, dict) for item in commands):
                errors.append(ValidationMessage(path, f"hook event must hold a list of mappings: {event}"))
                continue
            for command in commands:
                script = command.get("command")
                if not isinstance(script, str) or not script.strip():
                    errors.append(ValidationMessage(path, f"hook command must be a non-empty string: {event}"))
                elif not (root / script).exists():
                    errors.append(ValidationMessage(root / script, "hook command script does not exist"))
            events[event] = tuple(commands)

        if events:
            hooks.append(HookAsset(name=entry.slug, description=entry.description, path=path, events=events))
    return hooks


def _load_specs(root: Path) -> list[Path]:
    specs_root = root / SPECS_DIR
    if not specs_root.is_dir():
        return []
    return sorted(path for path in specs_root.rglob("*.md") if path.is_file())


def _read_json_mapping(path: Path, errors: list[ValidationMessage]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(ValidationMessage(path, "declared configuration file does not exist"))
        return None
    try:
        document = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(ValidationMessage(path, f"invalid JSON: {exc}"))
        return None
    if not isinstance(document, dict):
        errors.append(ValidationMessage(path, "expected a JSON object"))
        return None
    return document


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
