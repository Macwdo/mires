# Mires

Mires is an agent-first repository for AI runtime assets and owner-loaded reference skills. The canonical source tree is `.ai/`, and the Python tooling in `src/compatibility` validates those assets for supported runtime targets.

## Repository Layout

- `.ai/AGENTS.md`: public routing guide and runtime entrypoint documentation.
- `.ai/agents/<agent>/AGENT.md`: agent behavior, delegation rules, and front matter.
- `.ai/agents/<agent>/agents/openai.yaml`: runtime metadata for an agent.
- `.ai/skills/<skill>/SKILL.md`: owner-loaded skill guidance.
- `.ai/skills/<skill>/references/`: supporting reference material that is too detailed for the main skill file.
- `src/compatibility/`: runtime-agnostic asset parsing and target-specific validation.
- `scripts/verify_agent_first_surface.py`: repository-wide verification for the public `.ai` surface.

## Core Model

The repository uses orchestrator-first routing. For non-trivial engineering work, start from `.ai/agents/orchestrator/AGENT.md`; the orchestrator classifies the task and decides whether specialist agents should inspect before implementation.

Agents are public routing surfaces. Skills are reference packages loaded by an owning agent or workflow. Keep behavior and delegation rules in agents, and keep detailed patterns, examples, checklists, and anti-patterns in skills or their references.

## Local Checks

Run these commands from the repository root:

```bash
python3 scripts/verify_agent_first_surface.py
python3 src/main.py --target codex
```

Useful inspection commands:

```bash
rg --files .ai
sed -n '1,120p' .ai/agents/orchestrator/AGENT.md
sed -n '1,120p' .ai/skills/project-conventions/SKILL.md
git status --short
```

## Adding Or Changing Agents

When adding a public agent, update all related surfaces in the same change:

- `.ai/AGENTS.md`
- `.ai/agents/<agent>/AGENT.md`
- `.ai/agents/<agent>/agents/openai.yaml`
- `scripts/verify_agent_first_surface.py`

Agent front matter should include `name`, `description`, `parent`, and `children`. Keep directories lowercase kebab-case.

## Adding Or Changing Skills

Each skill must include a `SKILL.md` with YAML front matter:

```yaml
---
name: skill-name
description: Short trigger-oriented description.
---
```

Every skill should keep these sections:

- `## When To Use`
- `## Core Rules`
- `## Preferred Patterns`
- `## Anti-Patterns`
- `## Checklist`
- `## References Index`

If a skill references files under `references/`, make sure those paths exist and are listed in the skill's references index.

## Compatibility

The `.ai/agents` and `.ai/skills` trees are runtime-agnostic source assets. Runtime-specific checks belong in adapters under `src/compatibility`, starting with the Codex target.

Use `python3 src/main.py --target codex` to validate runtime compatibility. Use `python3 scripts/verify_agent_first_surface.py` for the broader repository surface check.

To install the canonical Mires agents into Codex, run:

```bash
python3 src/main.py install --target codex
```

This writes generated agent config layers to `$HOME/.codex/agents/`, registers them in `$HOME/.codex/config.toml` under `[agents.<agent-name>]` tables, and creates private agent bundles under `$HOME/.codex/mires/agents/<agent-name>/`. The canonical source remains `.ai/agents` and `.ai/skills`; files under `$HOME/.codex/agents/` and `$HOME/.codex/mires/` are generated runtime output.

Mires skill packages are bundled privately per agent. The installer does not write them to the global Codex skills directory, so unrelated Codex sessions do not inherit the full Mires reference set.

Preview the install without writing files:

```bash
python3 src/main.py install --target codex --dry-run
```

Use an isolated Codex home for tests or validation:

```bash
python3 src/main.py install --target codex --codex-home /tmp/mires-codex-home
```

## Security

Do not commit secrets, personal tokens, API keys, or private environment values in agent files, skill files, examples, metadata, or references. Use placeholder names such as `OPENAI_API_KEY` when configuration examples are needed.
