"""Renderers shared by every runtime target."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from mires.compatibility.models import AgentAsset, HookAsset, RuleAsset, SkillAsset

__all__ = [
    "agent_base_prompt",
    "agent_short_description",
    "hook_command_path",
    "referenced_skills",
    "rules_document",
    "yaml_string",
]

SKILL_REFERENCE_PATTERN = re.compile(r"`skills/([a-z0-9-]+)`")


def referenced_skills(agent: AgentAsset, skills_by_name: dict[str, SkillAsset]) -> tuple[SkillAsset, ...]:
    names = sorted(set(SKILL_REFERENCE_PATTERN.findall(agent.path.read_text())))
    return tuple(skills_by_name[name] for name in names if name in skills_by_name)


def agent_short_description(agent: AgentAsset) -> str:
    interface = _mapping(agent.metadata.get("interface"))
    return _string_value(interface.get("short_description")) or agent.description


def agent_base_prompt(agent: AgentAsset) -> str:
    interface = _mapping(agent.metadata.get("interface"))
    prompt = _string_value(interface.get("default_prompt")) or agent.description
    prefix = f"Use ${agent.name}. "
    return prompt[len(prefix) :] if prompt.startswith(prefix) else prompt


def rules_document(rules: tuple[RuleAsset, ...]) -> str:
    """The standing rules, rendered as one Markdown block for a shared instructions file.

    An empty catalog yields an empty string so the installer can clear the managed block.
    """
    if not rules:
        return ""
    lines = [
        "# Mires Rules",
        "",
        "Standing rules from the Mires catalog. They apply to every task unless the user overrides them.",
    ]
    for rule in rules:
        lines.extend(["", f"## {rule.name}", "", rule.description, "", _demote_headings(rule.body)])
    return "\n".join(lines)


def _demote_headings(body: str) -> str:
    """Push a rule's own headings below the section heading it is nested under."""
    return re.sub(r"(?m)^(#{1,4}) ", r"##\1 ", body)


def hook_command_path(hook: HookAsset, command: dict[str, Any], installed_dir: Path) -> str:
    """Resolve a hook command against its installed copy, so the runtime never points back at the repository."""
    script = str(command.get("command", "")).strip()
    if script.startswith(("/", "$", "~")):
        return script
    relative = Path(script)
    hook_prefix = Path("hooks") / hook.name
    if relative.is_relative_to(hook_prefix):
        relative = relative.relative_to(hook_prefix)
    return str(installed_dir / relative)


def yaml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
