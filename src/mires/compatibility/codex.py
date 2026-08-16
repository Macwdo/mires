from __future__ import annotations

import re
import shutil
import textwrap
import tomllib
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
    write_managed_markdown,
)

SUPPORTED_TARGET = "codex"
DISPLAY_NAME = "Codex"
CONFIG_FILE = "config.toml"
INSTRUCTIONS_FILE = "AGENTS.md"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
MIRES_DIR = "mires"
SPECS_DIR = "specs"
SOURCE_AGENTS_DIR = "subagents"
PROMPT_WRAP_WIDTH = 131

# Codex has no general hook runtime, so hooks are recorded in the bundle for
# reference but never registered.
UNSUPPORTED_KINDS = ("hooks",)


def default_home() -> Path:
    return Path.home() / ".codex"


def validate_codex(inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    errors: list[ValidationMessage] = list(inventory.errors)
    for agent in inventory.agents:
        metadata_path = agent.metadata_path or agent.path.parent / "agents" / "openai.yaml"
        metadata = agent.metadata
        interface = _mapping(metadata.get("interface"))
        runtime_metadata = _mapping(metadata.get("metadata"))

        _require_string(interface, "display_name", metadata_path, errors)
        _require_string(interface, "short_description", metadata_path, errors)
        _require_string(interface, "default_prompt", metadata_path, errors)
        codex_name = _require_string(runtime_metadata, "name", metadata_path, errors)
        if codex_name and codex_name != agent.name:
            errors.append(
                ValidationMessage(
                    metadata_path,
                    f"metadata.name must match agent front matter name: {agent.name}",
                )
            )

        children = runtime_metadata.get("children")
        if children is not None and not (
            isinstance(children, list) and all(isinstance(child, str) for child in children)
        ):
            errors.append(ValidationMessage(metadata_path, "metadata.children must be a list of strings"))

    return tuple(errors)


def check_target_supported(target: str, path: Path) -> tuple[ValidationMessage, ...]:
    if target == SUPPORTED_TARGET:
        return ()
    return (ValidationMessage(path, f"unsupported compatibility target: {target}"),)


def install_codex_assets(inventory: AssetInventory, codex_home: Path, dry_run: bool = False) -> InstallReport:
    agents = tuple(sorted(inventory.agents, key=lambda agent: agent.name))
    skills = tuple(sorted(inventory.skills, key=lambda skill: skill.name))
    skills_by_name = {skill.name: skill for skill in skills}
    bundle_plans = tuple((agent, referenced_skills(agent, skills_by_name)) for agent in agents)
    rendered_agents = tuple(
        (agent, render_agent_toml(agent, agent_skills, codex_home)) for agent, agent_skills in bundle_plans
    )
    previous = InstallManifest.load(codex_home)
    config_path = codex_home / CONFIG_FILE
    existing_config = config_path.read_text() if config_path.exists() else ""
    patched_config = patch_mcp_servers_config(
        patch_agents_config(existing_config, agents, previous.owned_keys("agents")),
        inventory.mcps,
        previous.owned_keys("mcp_servers"),
    )
    validate_install_output(rendered_agents, bundle_plans, patched_config)

    counts = {
        "subagents": len(agents),
        "skills": len(skills),
        "rules": len(inventory.rules),
        "mcps": len(inventory.mcps),
        "hooks": 0,
        "specs": len(inventory.specs),
    }
    if dry_run:
        print(f"Dry run: would install the Mires catalog into {codex_home}")
        for agent, agent_skills in bundle_plans:
            print(f"- would write {agent_file_path(codex_home, agent)}")
            print(f"- would refresh {agent_bundle_path(codex_home, agent)}")
            for skill in agent_skills:
                print(f"  - would bundle skill {skill.name}")
        for skill in skills:
            print(f"- would refresh {skill_package_path(codex_home, skill)}")
        if inventory.rules:
            print(f"- would update the Mires block in {codex_home / INSTRUCTIONS_FILE}")
        elif (codex_home / INSTRUCTIONS_FILE).exists():
            print(f"- would clear the Mires block in {codex_home / INSTRUCTIONS_FILE}")
        print(f"- would update {config_path}")
        return InstallReport(home=codex_home, counts=counts, unsupported=UNSUPPORTED_KINDS)

    manifest = InstallManifest(home=codex_home)

    agents_dir = codex_home / AGENTS_DIR
    agents_dir.mkdir(parents=True, exist_ok=True)
    remove_legacy_agent_bundle_root(codex_home)
    for agent, content in rendered_agents:
        path = agent_file_path(codex_home, agent)
        path.write_text(content)
        manifest.track_path(path)
    for agent, agent_skills in bundle_plans:
        write_agent_bundle(codex_home, agent, agent_skills)
        manifest.track_path(agent_bundle_path(codex_home, agent))

    for skill in skills:
        package = skill_package_path(codex_home, skill)
        copy_generated_tree(skill.path.parent, package)
        manifest.track_path(package)

    write_managed_markdown(codex_home / INSTRUCTIONS_FILE, rules_document(inventory.rules))

    if inventory.specs:
        specs_path = codex_home / MIRES_DIR / SPECS_DIR
        copy_generated_tree(inventory.root / "openspec" / "specs", specs_path)
        manifest.track_path(specs_path)

    codex_home.mkdir(parents=True, exist_ok=True)
    config_path.write_text(patched_config)
    manifest.track_keys("agents", [agent.name for agent in agents])
    manifest.track_keys("mcp_servers", [mcp.name for mcp in inventory.mcps])

    manifest.prune_stale_paths(previous)
    manifest.save()
    return InstallReport(home=codex_home, counts=counts, unsupported=UNSUPPORTED_KINDS)


def skill_package_path(codex_home: Path, skill: SkillAsset) -> Path:
    return codex_home / SKILLS_DIR / skill.name


def agent_file_path(codex_home: Path, agent: AgentAsset) -> Path:
    return codex_home / AGENTS_DIR / f"{agent.name}.toml"


def agent_bundle_path(codex_home: Path, agent: AgentAsset) -> Path:
    return codex_home / MIRES_DIR / AGENTS_DIR / agent.name


def remove_legacy_agent_bundle_root(codex_home: Path) -> None:
    legacy_path = codex_home / AGENTS_DIR / MIRES_DIR
    if legacy_path.exists():
        shutil.rmtree(legacy_path)


def render_agent_toml(
    agent: AgentAsset,
    skills: tuple[SkillAsset, ...] = (),
    codex_home: Path | None = None,
) -> str:
    codex_home = (codex_home or Path.home() / ".codex").expanduser().resolve()
    interface = _mapping(agent.metadata.get("interface"))
    base_prompt = normalize_default_prompt(_string_value(interface.get("default_prompt")) or agent.description, agent)
    instructions = render_developer_instructions(codex_home, agent, skills, base_prompt)

    lines = [
        "# Generated by Mires. Edit the canonical subagent source instead.",
        f'developer_instructions = """\n{_toml_multiline_escape(instructions)}\n"""',
    ]
    for skill in skills:
        lines.extend(
            [
                "",
                "[[skills.config]]",
                f'path = "{_toml_escape(str(agent_bundle_path(codex_home, agent) / "skills" / skill.name))}"',
                "enabled = true",
            ]
        )
    return "\n".join(lines) + "\n"


def render_developer_instructions(
    codex_home: Path,
    agent: AgentAsset,
    skills: tuple[SkillAsset, ...],
    base_prompt: str,
) -> str:
    bundle_path = str(agent_bundle_path(codex_home, agent))
    skill_lines = (
        "\n".join(f"- {bundle_path}/skills/{skill.name}" for skill in skills)
        if skills
        else "- No bundled skill packages are required for this agent."
    )
    prompt = f"""
You are the Mires {agent.name} agent.

Primary behavior:
{base_prompt}

Use the bundled agent instructions as the authoritative role guide:
{bundle_path}/AGENT.md

Work from the repository's existing conventions before introducing new patterns. Keep changes scoped to the
delegated task and report blockers, risks, and validation results clearly.

Load bundled skills only when they are relevant to the current task. Do not treat the bundled skills as global
session context. Available bundled skill packages:
{skill_lines}

The bundle is generated from the canonical Mires repository. Do not edit generated files directly; update the
Mires source assets and run the installer again.
"""
    return wrap_prompt(prompt.strip())


def write_agent_bundle(codex_home: Path, agent: AgentAsset, skills: tuple[SkillAsset, ...]) -> None:
    bundle_path = agent_bundle_path(codex_home, agent)
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    bundle_path.mkdir(parents=True, exist_ok=True)

    copy_generated_tree(agent.path.parent, bundle_path)
    skills_path = bundle_path / "skills"
    for skill in skills:
        copy_generated_tree(skill.path.parent, skills_path / skill.name)
    write_bundle_manifest(bundle_path, agent, skills)


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
    bundle_plans: tuple[tuple[AgentAsset, tuple[SkillAsset, ...]], ...],
    config_text: str,
) -> None:
    for agent, content in rendered_agents:
        try:
            parsed = tomllib.loads(content)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(f"generated Codex agent TOML is invalid for {agent.name}: {exc}") from exc
        if f"{SOURCE_AGENTS_DIR}/" in content:
            raise ValueError(f"generated Codex agent TOML contains repository-local source path for {agent.name}")
        unexpected = set(parsed) - {"developer_instructions", "agent_role", "skills"}
        if unexpected:
            raise ValueError(f"generated Codex agent TOML has unsupported keys for {agent.name}: {sorted(unexpected)}")
    for agent, skills in bundle_plans:
        if not agent.path.exists():
            raise ValueError(f"missing source agent file for {agent.name}: {agent.path}")
        if agent.metadata_path is None or not agent.metadata_path.exists():
            raise ValueError(f"missing source metadata file for {agent.name}")
        for skill in skills:
            if not skill.path.exists():
                raise ValueError(f"missing source skill file for {agent.name}: {skill.path}")
    try:
        if config_text.strip():
            tomllib.loads(config_text)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"patched Codex config TOML is invalid: {exc}") from exc


def patch_agents_config(
    config_text: str,
    agents: tuple[AgentAsset, ...],
    previous_names: list[str] | tuple[str, ...] = (),
) -> str:
    """Rewrite Mires-owned `[agents.<name>]` tables, including ones the last install left behind."""
    normalized = config_text.rstrip()
    blocks = [_agent_registration_block(agent) for agent in sorted(agents, key=lambda item: item.name)]
    without_managed = normalized
    for name in sorted({*previous_names, *(agent.name for agent in agents)}):
        without_managed = _remove_table(without_managed, f"agents.{name}")

    if _has_table(without_managed, "agents"):
        patched = without_managed.rstrip()
    elif blocks:
        patched = without_managed.rstrip()
        if patched:
            patched += "\n\n"
        patched += "[agents]"
    else:
        patched = without_managed.rstrip()

    if blocks:
        patched = patched.rstrip() + "\n\n" + "\n\n".join(blocks)
    return patched.rstrip() + "\n" if patched else ""


def patch_mcp_servers_config(
    config_text: str,
    mcps: tuple[McpAsset, ...],
    previous_names: list[str] | tuple[str, ...] = (),
) -> str:
    """Replace the `[mcp_servers.<name>]` tables Mires owns, leaving the user's own servers alone."""
    patched = config_text.rstrip()
    for name in sorted({*previous_names, *(mcp.name for mcp in mcps)}):
        patched = _remove_table(patched, f"mcp_servers.{name}")
    blocks = [_mcp_registration_block(mcp) for mcp in sorted(mcps, key=lambda item: item.name)]
    if blocks:
        patched = patched.rstrip() + "\n\n" + "\n\n".join(blocks)
    return patched.rstrip() + "\n" if patched else ""


def _mcp_registration_block(mcp: McpAsset) -> str:
    lines = [f"[mcp_servers.{mcp.name}]"]
    nested: list[str] = []
    for key, value in mcp.server.items():
        if isinstance(value, dict):
            nested.append(f"\n[mcp_servers.{mcp.name}.{key}]")
            nested.extend(f"{nested_key} = {_toml_value(nested_value)}" for nested_key, nested_value in value.items())
            continue
        lines.append(f"{key} = {_toml_value(value)}")
    return "\n".join(lines + nested)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        return _toml_string_array(tuple(str(item) for item in value))
    return f'"{_toml_escape(str(value))}"'


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _require_string(
    data: dict[str, Any],
    key: str,
    path: Path,
    errors: list[ValidationMessage],
) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    errors.append(ValidationMessage(path, f"missing required Codex metadata field: {key}"))
    return ""


def _agent_registration_block(agent: AgentAsset) -> str:
    interface = _mapping(agent.metadata.get("interface"))
    description = _string_value(interface.get("short_description")) or agent.description
    return "\n".join(
        [
            f"[agents.{agent.name}]",
            f'description = "{_toml_escape(description)}"',
            f'config_file = "agents/{_toml_escape(agent.name)}.toml"',
        ]
    )


def normalize_default_prompt(prompt: str, agent: AgentAsset) -> str:
    prefix = f"Use ${agent.name}. "
    if prompt.startswith(prefix):
        return prompt[len(prefix) :]
    return prompt


def _remove_table(text: str, table_name: str) -> str:
    """Drop a table and every sub-table beneath it, so a re-install never duplicates nested keys."""
    while True:
        match = _table_tree_pattern(table_name).search(text)
        if not match:
            return text
        start = match.start()
        next_match = _any_table_pattern().search(text, match.end())
        end = next_match.start() if next_match else len(text)
        before = text[:start].rstrip()
        after = text[end:].lstrip("\n")
        text = before + "\n\n" + after if before and after else before + after


def _has_table(text: str, table_name: str) -> bool:
    return _table_pattern(table_name).search(text) is not None


def _table_pattern(table_name: str) -> Any:
    return re.compile(rf"(?m)^\[{re.escape(table_name)}\]\s*$")


def _table_tree_pattern(table_name: str) -> Any:
    return re.compile(rf"(?m)^\[{re.escape(table_name)}(\.[^\]]+)?\]\s*$")


def _any_table_pattern() -> Any:
    return re.compile(r"(?m)^\[[^\]]+\]\s*$")


def _toml_string_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(f'"{_toml_escape(value)}"' for value in values) + "]"


def wrap_prompt(prompt: str) -> str:
    wrapped_blocks: list[str] = []
    for block in prompt.split("\n\n"):
        lines = block.splitlines()
        if len(lines) > 1 and all(line.startswith(("- ", "  ")) or not line.strip() for line in lines[1:]):
            wrapped_blocks.append("\n".join(_wrap_line(line) for line in lines))
        else:
            wrapped_blocks.append("\n".join(_wrap_line(line) for line in lines))
    return "\n\n".join(wrapped_blocks)


def _wrap_line(line: str) -> str:
    if not line.strip() or len(line) <= PROMPT_WRAP_WIDTH:
        return line
    if line.startswith("- "):
        return textwrap.fill(
            line,
            width=PROMPT_WRAP_WIDTH,
            subsequent_indent="  ",
            break_long_words=False,
            break_on_hyphens=False,
        )
    return textwrap.fill(line, width=PROMPT_WRAP_WIDTH, break_long_words=False, break_on_hyphens=False)


def _toml_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _toml_multiline_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
