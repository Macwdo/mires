from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from mires.compatibility.models import (
    AgentAsset,
    AssetInventory,
    InstallReport,
    McpAsset,
    SkillAsset,
    ValidationMessage,
)
from mires.compatibility.rendering import referenced_skills, rules_document
from mires.compatibility.writing import (
    InstallManifest,
    copy_generated_tree,
    read_json_object,
    write_json_object,
    write_managed_markdown,
)

SUPPORTED_TARGET = "opencode"
DISPLAY_NAME = "OpenCode"
PRIMARY_AGENT = "explorer"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
MIRES_DIR = "mires"
SPECS_DIR = "specs"
SKILL_FILE = "SKILL.md"
CONFIG_FILE = "opencode.json"
INSTRUCTIONS_FILE = "AGENTS.md"
SOURCE_AGENTS_DIR = "subagents"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# OpenCode has no user-level hook runtime of its own.
UNSUPPORTED_KINDS = ("hooks",)


def default_home() -> Path:
    return Path.home() / ".config" / "opencode"


def validate_opencode(inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    errors: list[ValidationMessage] = list(inventory.errors)
    for agent in inventory.agents:
        _validate_name(agent.name, agent.path, "agent", errors)
        if not agent.description.strip():
            errors.append(ValidationMessage(agent.path, "missing OpenCode agent description"))
    for skill in inventory.skills:
        _validate_name(skill.name, skill.path, "skill", errors)
        if not skill.description.strip():
            errors.append(ValidationMessage(skill.path, "missing OpenCode skill description"))
        if len(skill.description) > 1024:
            errors.append(ValidationMessage(skill.path, "OpenCode skill description exceeds 1024 characters"))
    return tuple(errors)


def install_opencode_assets(inventory: AssetInventory, opencode_home: Path, dry_run: bool = False) -> InstallReport:
    agents = tuple(sorted(inventory.agents, key=lambda agent: agent.name))
    skills = tuple(sorted(inventory.skills, key=lambda skill: skill.name))
    skills_by_name = {skill.name: skill for skill in skills}
    bundle_plans = tuple((agent, referenced_skills(agent, skills_by_name)) for agent in agents)
    rendered_agents = tuple(
        (agent, render_agent_markdown(agent, agent_skills, opencode_home)) for agent, agent_skills in bundle_plans
    )
    rendered_skills = tuple((skill, render_skill_markdown(skill)) for skill in skills)
    validate_install_output(rendered_agents, rendered_skills, bundle_plans)

    counts = {
        "subagents": len(agents),
        "skills": len(skills),
        "rules": len(inventory.rules),
        "mcps": len(inventory.mcps),
        "hooks": 0,
        "specs": len(inventory.specs),
    }
    if dry_run:
        print(f"Dry run: would install the Mires catalog into {opencode_home}")
        for agent, agent_skills in bundle_plans:
            print(f"- would write {agent_file_path(opencode_home, agent)}")
            print(f"- would refresh {agent_bundle_path(opencode_home, agent)}")
            for skill in agent_skills:
                print(f"  - agent may load skill {skill.name}")
        for skill in skills:
            print(f"- would refresh {skill_package_path(opencode_home, skill)}")
        if inventory.rules:
            print(f"- would update the Mires block in {opencode_home / INSTRUCTIONS_FILE}")
        if inventory.mcps:
            print(f"- would register {len(inventory.mcps)} MCP servers in {opencode_home / CONFIG_FILE}")
        return InstallReport(home=opencode_home, counts=counts, unsupported=UNSUPPORTED_KINDS)

    previous = InstallManifest.load(opencode_home)
    manifest = InstallManifest(home=opencode_home)

    agents_path = opencode_home / AGENTS_DIR
    agents_path.mkdir(parents=True, exist_ok=True)
    for agent, content in rendered_agents:
        path = agent_file_path(opencode_home, agent)
        path.write_text(content)
        manifest.track_path(path)
    for agent, agent_skills in bundle_plans:
        write_agent_bundle(opencode_home, agent, agent_skills)
        manifest.track_path(agent_bundle_path(opencode_home, agent))
    for skill, content in rendered_skills:
        write_skill_package(opencode_home, skill, content)
        manifest.track_path(skill_package_path(opencode_home, skill))

    if inventory.rules:
        write_managed_markdown(opencode_home / INSTRUCTIONS_FILE, rules_document(inventory.rules))

    if inventory.specs:
        specs_path = opencode_home / MIRES_DIR / SPECS_DIR
        copy_generated_tree(inventory.root / "openspec" / "specs", specs_path)
        manifest.track_path(specs_path)

    write_mcp_servers(opencode_home, inventory.mcps, previous, manifest)

    manifest.prune_stale_paths(previous)
    manifest.save()
    return InstallReport(home=opencode_home, counts=counts, unsupported=UNSUPPORTED_KINDS)


def write_mcp_servers(
    opencode_home: Path,
    mcps: tuple[McpAsset, ...],
    previous: InstallManifest,
    manifest: InstallManifest,
) -> None:
    """OpenCode nests MCP servers under `mcp` and tags each with a transport type."""
    path = opencode_home / CONFIG_FILE
    document = read_json_object(path)
    servers = dict(document.get("mcp") or {})

    for stale in previous.owned_keys("mcp"):
        servers.pop(stale, None)
    for mcp in mcps:
        if mcp.is_remote:
            entry: dict[str, Any] = {"type": "remote", "url": mcp.server["url"], "enabled": True}
        else:
            command = [mcp.server["command"], *(mcp.server.get("args") or [])]
            entry = {"type": "local", "command": command, "enabled": True}
            if mcp.server.get("env"):
                entry["environment"] = mcp.server["env"]
        servers[mcp.name] = entry

    document["mcp"] = servers
    document.setdefault("$schema", "https://opencode.ai/config.json")
    write_json_object(path, document)
    manifest.track_keys("mcp", [mcp.name for mcp in mcps])


def agent_file_path(opencode_home: Path, agent: AgentAsset) -> Path:
    return opencode_home / AGENTS_DIR / f"{agent.name}.md"


def agent_bundle_path(opencode_home: Path, agent: AgentAsset) -> Path:
    return opencode_home / MIRES_DIR / AGENTS_DIR / agent.name


def skill_package_path(opencode_home: Path, skill: SkillAsset) -> Path:
    return opencode_home / SKILLS_DIR / skill.name


def render_agent_markdown(
    agent: AgentAsset,
    skills: tuple[SkillAsset, ...] = (),
    opencode_home: Path | None = None,
) -> str:
    opencode_home = (opencode_home or Path.home() / ".config" / "opencode").expanduser().resolve()
    interface = _mapping(agent.metadata.get("interface"))
    base_prompt = normalize_default_prompt(_string_value(interface.get("default_prompt")) or agent.description, agent)
    instructions = render_agent_instructions(opencode_home, agent, skills, base_prompt)
    description = _string_value(interface.get("short_description")) or agent.description
    return "\n".join(
        [
            "---",
            f"description: {_yaml_string(description)}",
            f"mode: {agent_mode(agent)}",
            "---",
            instructions,
            "",
        ]
    )


def render_agent_instructions(
    opencode_home: Path,
    agent: AgentAsset,
    skills: tuple[SkillAsset, ...],
    base_prompt: str,
) -> str:
    bundle_path = str(agent_bundle_path(opencode_home, agent))
    skill_lines = (
        "\n".join(f"- {skill.name}" for skill in skills)
        if skills
        else "- No Mires skills are required for this agent."
    )
    return f"""
You are the Mires {agent.name} agent.

Primary behavior:
{base_prompt}

Use the generated agent instructions as the authoritative role guide:
{bundle_path}/AGENT.md

Work from the repository's existing conventions before introducing new patterns. Keep changes scoped to the
delegated task and report blockers, risks, and validation results clearly.

Load Mires skills only when they are relevant to the current task. Available generated OpenCode skill packages:
{skill_lines}

This file is generated by Mires. Do not edit generated files directly; update the Mires source assets and run
the installer again.
""".strip()


def render_skill_markdown(skill: SkillAsset) -> str:
    return add_generated_note(skill.path.read_text(), "skill")


def agent_mode(agent: AgentAsset) -> str:
    return "primary" if agent.name == PRIMARY_AGENT else "subagent"


def write_agent_bundle(opencode_home: Path, agent: AgentAsset, skills: tuple[SkillAsset, ...]) -> None:
    bundle_path = agent_bundle_path(opencode_home, agent)
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    bundle_path.mkdir(parents=True, exist_ok=True)

    copy_generated_tree(agent.path.parent, bundle_path)
    write_bundle_manifest(bundle_path, agent, skills)


def write_skill_package(opencode_home: Path, skill: SkillAsset, skill_content: str) -> None:
    package_path = skill_package_path(opencode_home, skill)
    if package_path.exists():
        shutil.rmtree(package_path)
    package_path.mkdir(parents=True, exist_ok=True)
    copy_generated_tree(skill.path.parent, package_path)
    (package_path / SKILL_FILE).write_text(skill_content)


def write_bundle_manifest(bundle_path: Path, agent: AgentAsset, skills: tuple[SkillAsset, ...]) -> None:
    lines = [
        "# Generated by Mires",
        "",
        f"- Agent: {agent.name}",
        f"- Skills: {', '.join(skill.name for skill in skills) if skills else 'none'}",
    ]
    (bundle_path / "MANIFEST.md").write_text("\n".join(lines) + "\n")


def validate_install_output(
    rendered_agents: tuple[tuple[AgentAsset, str], ...],
    rendered_skills: tuple[tuple[SkillAsset, str], ...],
    bundle_plans: tuple[tuple[AgentAsset, tuple[SkillAsset, ...]], ...],
) -> None:
    for agent, content in rendered_agents:
        if f"{SOURCE_AGENTS_DIR}/" in content:
            raise ValueError(f"generated OpenCode agent contains repository-local source path for {agent.name}")
        frontmatter = _frontmatter(content)
        if _string_value(frontmatter.get("description")) == "":
            raise ValueError(f"generated OpenCode agent is missing description for {agent.name}")
        if frontmatter.get("mode") not in {"primary", "subagent", "all"}:
            raise ValueError(f"generated OpenCode agent has unsupported mode for {agent.name}")
    for skill, content in rendered_skills:
        if f"{SOURCE_AGENTS_DIR}/" in content:
            raise ValueError(f"generated OpenCode skill contains repository-local source path for {skill.name}")
        frontmatter = _frontmatter(content)
        if frontmatter.get("name") != skill.name:
            raise ValueError(f"generated OpenCode skill name mismatch for {skill.name}")
        if _string_value(frontmatter.get("description")) == "":
            raise ValueError(f"generated OpenCode skill is missing description for {skill.name}")
    for agent, skills in bundle_plans:
        if not agent.path.exists():
            raise ValueError(f"missing source agent file for {agent.name}: {agent.path}")
        for skill in skills:
            if not skill.path.exists():
                raise ValueError(f"missing source skill file for {agent.name}: {skill.path}")


def add_generated_note(text: str, asset_type: str) -> str:
    if not text.startswith("---\n"):
        return f"<!-- Generated by Mires for OpenCode. Edit canonical Mires source assets instead. -->\n\n{text}"
    end = text.find("\n---", 4)
    if end == -1:
        return text
    insert_at = end + len("\n---")
    note = f"\n\n<!-- Generated by Mires for OpenCode. Edit canonical Mires {asset_type} source assets instead. -->"
    return text[:insert_at] + note + text[insert_at:]


def normalize_default_prompt(prompt: str, agent: AgentAsset) -> str:
    prefix = f"Use ${agent.name}. "
    if prompt.startswith(prefix):
        return prompt[len(prefix) :]
    return prompt


def _validate_name(name: str, path: Path, asset_type: str, errors: list[ValidationMessage]) -> None:
    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append(ValidationMessage(path, f"invalid OpenCode {asset_type} name: {name}"))


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("generated OpenCode Markdown is missing front matter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("generated OpenCode Markdown has unterminated front matter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"generated OpenCode Markdown has invalid front matter line: {line}")
        key, raw_value = line.split(":", 1)
        values[key.strip()] = raw_value.strip().strip('"')
    return values


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _yaml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
