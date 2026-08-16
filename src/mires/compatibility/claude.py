"""Install the Mires catalog into Claude Code.

Claude Code splits its user configuration across several files: subagents and
skills are directories under `~/.claude`, MCP servers live at user scope in
`~/.claude.json`, hooks live in `~/.claude/settings.json`, and standing
instructions live in `~/.claude/CLAUDE.md`. All four are shared with the user,
so each write is scoped to what Mires owns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mires.compatibility.models import (
    AgentAsset,
    AssetInventory,
    HookAsset,
    InstallReport,
    McpAsset,
    SkillAsset,
    ValidationMessage,
)
from mires.compatibility.rendering import (
    agent_base_prompt,
    agent_short_description,
    hook_command_path,
    referenced_skills,
    rules_document,
    yaml_string,
)
from mires.compatibility.writing import (
    GENERATED_NOTICE,
    InstallManifest,
    copy_generated_tree,
    install_hook_scripts,
    read_json_object,
    write_json_object,
    write_managed_markdown,
)

SUPPORTED_TARGET = "claude"
DISPLAY_NAME = "Claude Code"
AGENTS_DIR = "agents"
SKILLS_DIR = "skills"
MIRES_DIR = "mires"
SPECS_DIR = "specs"
MEMORY_FILE = "CLAUDE.md"
SETTINGS_FILE = "settings.json"
SOURCE_AGENTS_DIR = "subagents"

# Claude Code keys user-scope MCP servers out of the home directory, not out of
# the `.claude` directory, so it does not move with `--claude-home`.
USER_CONFIG_FILE = ".claude.json"

# Canonical Mires event -> (Claude event, tool matcher). Claude routes tool
# lifecycle hooks through matchers instead of dedicated event names.
HOOK_EVENTS: dict[str, tuple[str, str]] = {
    "beforeSubmitPrompt": ("UserPromptSubmit", ""),
    "beforeShellExecution": ("PreToolUse", "Bash"),
    "beforeReadFile": ("PreToolUse", "Read"),
    "afterFileEdit": ("PostToolUse", "Edit|Write|MultiEdit|NotebookEdit"),
    "stop": ("Stop", ""),
}


def default_home() -> Path:
    return Path.home() / ".claude"


def validate_claude(inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    errors: list[ValidationMessage] = list(inventory.errors)
    for agent in inventory.agents:
        if not agent.description.strip():
            errors.append(ValidationMessage(agent.path, "missing Claude subagent description"))
    for skill in inventory.skills:
        if not skill.description.strip():
            errors.append(ValidationMessage(skill.path, "missing Claude skill description"))
    for mcp in inventory.mcps:
        if mcp.is_remote and not str(mcp.server.get("url", "")).startswith(("http://", "https://")):
            errors.append(ValidationMessage(mcp.path, "remote MCP server url must be http or https"))
    return tuple(errors)


def install_claude_assets(inventory: AssetInventory, home: Path, dry_run: bool = False) -> InstallReport:
    agents = tuple(sorted(inventory.agents, key=lambda agent: agent.name))
    skills = tuple(sorted(inventory.skills, key=lambda skill: skill.name))
    skills_by_name = {skill.name: skill for skill in skills}
    rendered_agents = tuple(
        (agent, render_subagent(agent, referenced_skills(agent, skills_by_name))) for agent in agents
    )

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
            print(f"- would write {subagent_path(home, agent)}")
        for skill in skills:
            print(f"- would refresh {skill_path(home, skill)}")
        if inventory.rules:
            print(f"- would update the Mires block in {home / MEMORY_FILE}")
        elif (home / MEMORY_FILE).exists():
            print(f"- would clear the Mires block in {home / MEMORY_FILE}")
        if inventory.mcps:
            print(f"- would register {len(inventory.mcps)} MCP servers in {user_config_path(home)}")
        if inventory.hooks:
            print(f"- would register hooks in {home / SETTINGS_FILE}")
        return InstallReport(home=home, counts=counts)

    previous = InstallManifest.load(home)
    manifest = InstallManifest(home=home)

    for agent, content in rendered_agents:
        path = subagent_path(home, agent)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        manifest.track_path(path)

    for skill in skills:
        path = skill_path(home, skill)
        copy_generated_tree(skill.path.parent, path)
        manifest.track_path(path)

    write_managed_markdown(home / MEMORY_FILE, rules_document(inventory.rules))

    if inventory.specs:
        specs_path = home / MIRES_DIR / SPECS_DIR
        copy_generated_tree(inventory.root / "openspec" / "specs", specs_path)
        manifest.track_path(specs_path)

    write_mcp_servers(home, inventory.mcps, previous, manifest)
    write_hooks(home, inventory.hooks, install_hook_scripts(home, inventory.hooks, manifest), previous, manifest)

    manifest.prune_stale_paths(previous)
    manifest.save()
    return InstallReport(home=home, counts=counts)


def subagent_path(home: Path, agent: AgentAsset) -> Path:
    return home / AGENTS_DIR / f"{agent.name}.md"


def skill_path(home: Path, skill: SkillAsset) -> Path:
    return home / SKILLS_DIR / skill.name


def user_config_path(home: Path) -> Path:
    """`~/.claude.json` normally, or a sibling of an isolated home during tests."""
    if home == default_home():
        return Path.home() / USER_CONFIG_FILE
    return home.parent / USER_CONFIG_FILE


def render_subagent(agent: AgentAsset, skills: tuple[SkillAsset, ...]) -> str:
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


def write_mcp_servers(
    home: Path,
    mcps: tuple[McpAsset, ...],
    previous: InstallManifest,
    manifest: InstallManifest,
) -> None:
    path = user_config_path(home)
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
    path = home / SETTINGS_FILE
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
        for canonical, commands in sorted(hook.events.items()):
            mapping = HOOK_EVENTS.get(canonical)
            if mapping is None:
                continue
            event, matcher = mapping
            entry: dict[str, Any] = {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command_path(hook, command, installed_scripts[hook.name]),
                        **({"timeout": command["timeout"]} if "timeout" in command else {}),
                    }
                    for command in commands
                ],
                "mires": hook.name,
            }
            if matcher:
                entry["matcher"] = matcher
            configured.setdefault(event, []).append(entry)
            identifiers.append(_identifier(event, entry))

    if configured:
        document["hooks"] = configured
    else:
        document.pop("hooks", None)
    write_json_object(path, document)
    manifest.track_keys("hooks", identifiers)


def _identifier(event: str, entry: Any) -> str:
    owner = entry.get("mires") if isinstance(entry, dict) else None
    matcher = entry.get("matcher", "") if isinstance(entry, dict) else ""
    return f"{event}:{matcher}:{owner}" if owner else ""
