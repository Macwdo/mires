# Repository Guidelines

Mires is a Markdown-only repository. Every tracked file ends in `.md`. Mires is runtime-agnostic: skills, rules, and agent prompts work in OpenBot, Claude Code, Devin, and other agents; see `RUNTIMES.md`. `CLAUDE.md` only imports this file. The agents run on OpenBot; see `openbot/README.md`, and `MIRES-OPENBOT.md` for recreating them in a local OpenBot. Skills install with `npx skills add Macwdo/mires` (or `bunx`).

## Structure

- `skills/<slug>/SKILL.md`: one skill per folder, with front matter `name` (equal to the folder slug) and `description`. Each skill is one file. `skills/mires/SKILL.md` is the index that points to every other skill; update it when a skill is added.
- `openbot/agents/<slug>.md`: one OpenBot agent profile per file. Update it when the agent changes in OpenBot.
- `subagents/<slug>/AGENT.md`: pre-OpenBot role prompts, kept as reference.
- `rules/<slug>.md`: standing rules.
- `RUNTIMES.md`: how each runtime installs Mires, and the map from capabilities to each runtime's tools.

Skills reference one another by `$slug`. Keep directory names lowercase kebab-case. Skills describe capabilities, not one runtime's MCP tools; see `rules/runtime-agnostic.md`.

## OpenBot

C'est Moi is the master agent and coordinator. Only it changes agent rules, memory, and skills, at the owner's request. Never commit employer-specific agents, paths, or data: this repository is public.

## Reference Subagents

- `mires-technical-context-explorer`: map files, entrypoints, dependencies, and technical constraints. Read-only.
- `mires-technical-standards-reviewer`: compare code with repository evidence and classify patterns and drift. Read-only.
- `mires-business-context-explorer`: discover actors, workflows, business rules, and POC hypotheses. Read-only.
- `mires-business-rules-reviewer`: review requirements, rules, and POC readiness. Read-only.
- `planner`: turn an ambiguous request into a decision-ready plan.

## Rules For All Work

- Inspect existing code patterns before proposing new ones.
- Prefer project conventions over generic advice.
- Separate discovered constraints from assumptions.
- Only one agent should modify files for a given change.

## Commits

Use short imperative commit subjects. See `rules/commit-style.md`. Never commit secrets; see `rules/no-secrets.md`.
