# Runtimes

Mires is runtime-agnostic. Skills, rules, and agent prompts are plain Markdown and describe capabilities (open a page, take a screenshot, delegate a review), not the MCP tools of one runtime. Each runtime maps those capabilities to its own tools.

## Pieces And Where They Go

| Piece | OpenBot | Claude Code | Devin |
| --- | --- | --- | --- |
| Repository guide (`AGENTS.md`) | Agent workspace `AGENTS.md` | Read through `CLAUDE.md` (`@AGENTS.md`) | Read automatically |
| Skills (`skills/`) | `openbot.create_skill`, see `MIRES-OPENBOT.md` | `npx skills add Macwdo/mires --all -a claude-code` | `npx skills add Macwdo/mires --all -a devin`, or upload as Devin skills |
| Agents (`openbot/agents/`, `subagents/`) | OpenBot agents, see `MIRES-OPENBOT.md` | Subagents in `.claude/agents/<slug>.md` | Playbooks, or prompts for child sessions |
| Rules (`rules/`) | Master agent instructions | `CLAUDE.md` or `.claude/rules/` | `AGENTS.md`, or Devin knowledge |
| Browser and screenshots | `openbot_browser` MCP + Computer Use | Playwright MCP (or Chrome DevTools MCP) | Native browser, no MCP needed |

Any other agent supported by the [skills CLI](https://github.com/vercel-labs/skills) installs skills with `-a <agent>`.

## Capabilities

Skills only name these capabilities. The table is the single place that maps them to tools.

| Capability | Used by | OpenBot | Claude Code | Devin |
| --- | --- | --- | --- | --- |
| Browser: open, read, screenshot | `$navegador-e-prints` | `openbot_browser.*`, Computer Use | Playwright MCP | Native browser (`computer` tool) |
| Delegate to another agent | `$mires`, `subagents/` | Channels and agent messages | Subagents (Task tool) | Subagents or child sessions |
| Agent management | `MIRES-OPENBOT.md` | `openbot.*` | Not applicable | Not applicable |

When a capability is missing, the agent says so and continues from evidence it has; it never claims a check it could not run.

## Claude Code

1. Skills, per project or globally (`-g`):

   ```bash
   npx skills add Macwdo/mires --all -a claude-code
   ```

2. Browser MCP for `$navegador-e-prints`:

   ```bash
   claude mcp add playwright -- npx @playwright/mcp@latest
   ```

3. Agents: copy a file from `subagents/<slug>/AGENT.md` or `openbot/agents/<slug>.md` to `.claude/agents/<slug>.md`. Keep `name` and `description` in the front matter, drop the OpenBot-only keys (`runtime`, `provider`, `display_name`, `title`, `reasoning_effort`, `skills`), and set `model` only to a model Claude Code lists.

## Devin

1. Devin reads `AGENTS.md` and `CLAUDE.md` from the repository it works in, with no setup.
2. Skills: in the target project, run `npx skills add Macwdo/mires --all -a devin` and commit `.devin/skills/`, or add the `skills/<slug>/SKILL.md` files as personal or organization skills in Devin. For Devin for Terminal, add `-g` to install into `~/.config/devin/skills/`.
3. Browser: `$navegador-e-prints` uses Devin's built-in browser and screenshots; no MCP is required.
4. Agents: Devin has no persistent agent team. Use an agent file's body as a playbook, or as the prompt for a subagent or child session.
5. Other MCP servers, if a project needs them, are added in Devin's MCP settings.

## OpenBot

Follow [`MIRES-OPENBOT.md`](MIRES-OPENBOT.md). The `runtime`, `provider`, `model`, and `reasoning_effort` keys in `openbot/agents/*.md` apply only to OpenBot; the profile text is runtime-neutral.
