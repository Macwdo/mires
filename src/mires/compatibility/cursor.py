"""Install the Mires catalog into Cursor.

Cursor keeps most user configuration under `~/.cursor`: skills and agents as
directories, MCP servers in `mcp.json`, and hooks in `hooks.json`. Its hook event
names are the ones Mires uses canonically, so hooks map straight through.

Rules are the exception. Cursor has no global rules directory: User Rules live in
its settings store, and only project rules are loaded from `.mdc` files. The one
documented way to ship rules globally from the filesystem is a local plugin, so
that is where they go. Unlike `mcp.json` and `hooks.json`, which Cursor watches
and reloads on save, a plugin is picked up on window reload.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from mires.compatibility.models import (
    AgentAsset,
    AssetInventory,
    HookAsset,
    InstallReport,
    McpAsset,
    RuleAsset,
    SkillAsset,
    ValidationMessage,
)
from mires.compatibility.rendering import (
    agent_base_prompt,
    agent_short_description,
    hook_command_path,
    referenced_skills,
    yaml_string,
)
from mires.compatibility.writing import (
    GENERATED_NOTICE,
    InstallManifest,
    copy_generated_tree,
    install_hook_scripts,
    read_json_object,
    write_json_object,
)

SUPPORTED_TARGET = "cursor"
DISPLAY_NAME = "Cursor"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
MIRES_DIR = "mires"
SPECS_DIR = "specs"
MCP_FILE = "mcp.json"
HOOKS_FILE = "hooks.json"
HOOKS_SCHEMA_VERSION = 1

PLUGIN_NAME = "mires"
PLUGIN_DIR = Path("plugins") / "local" / PLUGIN_NAME
PLUGIN_MANIFEST = Path(".cursor-plugin") / "plugin.json"
PLUGIN_RULES_DIR = "rules"

# Cursor's own event vocabulary matches the canonical Mires names one to one.
HOOK_EVENTS = ("beforeSubmitPrompt", "beforeShellExecution", "beforeReadFile", "afterFileEdit", "stop")


def default_home() -> Path:
    return Path.home() / ".cursor"


def validate_cursor(inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    errors: list[ValidationMessage] = list(inventory.errors)
    for agent in inventory.agents:
        if not agent.description.strip():
            errors.append(ValidationMessage(agent.path, "missing Cursor agent description"))
    for skill in inventory.skills:
        if not skill.description.strip():
            errors.append(ValidationMessage(skill.path, "missing Cursor skill description"))
    for hook in inventory.hooks:
        for event in hook.events:
            if event not in HOOK_EVENTS:
                errors.append(ValidationMessage(hook.path, f"Cursor does not support hook event: {event}"))
    return tuple(errors)


def install_cursor_assets(inventory: AssetInventory, home: Path, dry_run: bool = False) -> InstallReport:
    agents = tuple(sorted(inventory.agents, key=lambda agent: agent.name))
    skills = tuple(sorted(inventory.skills, key=lambda skill: skill.name))
    skills_by_name = {skill.name: skill for skill in skills}
    rendered_agents = tuple((agent, render_agent(agent, referenced_skills(agent, skills_by_name))) for agent in agents)

    counts = {
        "subagents": len(agents),
        "skills": len(skills),
        "rules": len(inventory.rules),
        "mcps": len(inventory.mcps),
        "hooks": sum(len(hook.events) for hook in inventory.hooks),
        "specs": len(inventory.specs),
    }
    if dry_run:
        print(f"Dry run: would install the Mires catalog into {home}")
        for agent, _ in rendered_agents:
            print(f"- would write {agent_path(home, agent)}")
        for skill in skills:
            print(f"- would refresh {skill_path(home, skill)}")
        for rule in inventory.rules:
            print(f"- would write {rule_path(home, rule)}")
        if inventory.mcps:
            print(f"- would register {len(inventory.mcps)} MCP servers in {home / MCP_FILE}")
        if inventory.hooks:
            print(f"- would register hooks in {home / HOOKS_FILE}")
        return InstallReport(home=home, counts=counts)

    previous = InstallManifest.load(home)
    manifest = InstallManifest(home=home)

    for agent, content in rendered_agents:
        path = agent_path(home, agent)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        manifest.track_path(path)

    for skill in skills:
        path = skill_path(home, skill)
        copy_generated_tree(skill.path.parent, path)
        manifest.track_path(path)

    write_rules_plugin(home, inventory.rules, manifest)

    if inventory.specs:
        specs_path = home / MIRES_DIR / SPECS_DIR
        copy_generated_tree(inventory.root / "openspec" / "specs", specs_path)
        manifest.track_path(specs_path)

    write_mcp_servers(home, inventory.mcps, previous, manifest)
    write_hooks(home, inventory.hooks, install_hook_scripts(home, inventory.hooks, manifest), previous, manifest)

    manifest.prune_stale_paths(previous)
    manifest.save()
    return InstallReport(home=home, counts=counts)


def agent_path(home: Path, agent: AgentAsset) -> Path:
    return home / AGENTS_DIR / f"{agent.name}.md"


def skill_path(home: Path, skill: SkillAsset) -> Path:
    return home / SKILLS_DIR / skill.name


def rule_path(home: Path, rule: RuleAsset) -> Path:
    return home / PLUGIN_DIR / PLUGIN_RULES_DIR / f"{rule.name}.mdc"


def write_rules_plugin(home: Path, rules: tuple[RuleAsset, ...], manifest: InstallManifest) -> None:
    """Rules reach Cursor globally only through a local plugin, so Mires ships one."""
    plugin_root = home / PLUGIN_DIR
    rules_root = plugin_root / PLUGIN_RULES_DIR
    if rules_root.exists():
        shutil.rmtree(rules_root)
    if not rules:
        return

    manifest_path = plugin_root / PLUGIN_MANIFEST
    write_json_object(
        manifest_path,
        {
            "name": PLUGIN_NAME,
            "displayName": "Mires",
            "description": "Standing rules from the Mires catalog.",
            "version": "1.0.0",
        },
    )
    manifest.track_path(plugin_root)

    for rule in rules:
        path = rule_path(home, rule)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_rule(rule))


def render_agent(agent: AgentAsset, skills: tuple[SkillAsset, ...]) -> str:
    body = agent.path.read_text()
    _, _, remainder = body.partition("---")
    _, _, instructions = remainder.partition("---")
    skill_lines = (
        "\n".join(f"- {skill.name}" for skill in skills) if skills else "- No Mires skills are required for this agent."
    )
    return "\n".join(
        [
            "---",
            f"name: {agent.name}",
            f"description: {yaml_string(agent_short_description(agent))}",
            "---",
            "",
            f"<!-- {GENERATED_NOTICE} -->",
            "",
            f"You are the Mires {agent.name} agent.",
            "",
            "Primary behavior:",
            agent_base_prompt(agent),
            "",
            instructions.strip(),
            "",
            "## Available Mires Skills",
            "",
            skill_lines,
            "",
        ]
    )


def render_rule(rule: RuleAsset) -> str:
    return "\n".join(
        [
            "---",
            f"description: {yaml_string(rule.description)}",
            "alwaysApply: true",
            "---",
            "",
            f"<!-- {GENERATED_NOTICE} -->",
            "",
            rule.body,
            "",
        ]
    )


def write_mcp_servers(
    home: Path,
    mcps: tuple[McpAsset, ...],
    previous: InstallManifest,
    manifest: InstallManifest,
) -> None:
    path = home / MCP_FILE
    document = read_json_object(path)
    servers = dict(document.get("mcpServers") or {})

    for stale in previous.owned_keys("mcpServers"):
        servers.pop(stale, None)
    for mcp in mcps:
        servers[mcp.name] = dict(mcp.server)

    document["mcpServers"] = servers
    write_json_object(path, document)
    manifest.track_keys("mcpServers", [mcp.name for mcp in mcps])


def write_hooks(
    home: Path,
    hooks: tuple[HookAsset, ...],
    installed_scripts: dict[str, Path],
    previous: InstallManifest,
    manifest: InstallManifest,
) -> None:
    path = home / HOOKS_FILE
    document = read_json_object(path)
    configured: dict[str, Any] = dict(document.get("hooks") or {})

    owned = set(previous.owned_keys("hooks"))
    for event, entries in list(configured.items()):
        if not isinstance(entries, list):
            continue
        kept = [entry for entry in entries if _identifier(event, entry) not in owned]
        if kept:
            configured[event] = kept
        else:
            configured.pop(event, None)

    identifiers: list[str] = []
    for hook in hooks:
        for event, commands in sorted(hook.events.items()):
            for command in commands:
                entry = {
                    key: value
                    for key, value in command.items()
                    if key in {"type", "timeout", "matcher", "failClosed", "loop_limit"}
                }
                entry["command"] = hook_command_path(hook, command, installed_scripts[hook.name])
                entry["mires"] = hook.name
                configured.setdefault(event, []).append(entry)
                identifiers.append(_identifier(event, entry))

    document["version"] = HOOKS_SCHEMA_VERSION
    if configured:
        document["hooks"] = configured
    else:
        document.pop("hooks", None)
    write_json_object(path, document)
    manifest.track_keys("hooks", identifiers)


def _identifier(event: str, entry: Any) -> str:
    if not isinstance(entry, dict) or "mires" not in entry:
        return ""
    return f"{event}:{entry.get('command', '')}:{entry['mires']}"
