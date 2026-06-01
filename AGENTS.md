# Repository Guidelines

## Orchestrator-First Routing

For non-trivial engineering work in this repository, route through `.ai/agents/orchestrator/AGENT.md` first.

- The user should not need to manually request subagents.
- The orchestrator decides whether delegation is needed.
- Simple tasks can be handled directly.
- Medium and complex tasks should be delegated to specialist agents.
- Most specialist agents should inspect and report before implementation starts.
- Only one final implementation agent should modify files after findings are merged.
- Prefer project conventions over generic advice.
- Always inspect existing code patterns before proposing new ones.

## Project Structure & Module Organization

This repository stores Mires AI agents and owner-loaded reference skills. The canonical authoring layout lives under `.ai/`:

- `.ai/AGENTS.md`: runtime routing guide with orchestrator-first behavior.
- `.ai/agents/<agent-name>/`: agent entrypoints, delegation rules, and runtime metadata.
- `.ai/skills/<skill-name>/`: agent-owned reference packages and detailed supporting material.

Each skill should include a `SKILL.md` with YAML front matter (`name`, `description`) followed by concise Markdown instructions for the owning agent or workflow. Each agent should include an `AGENT.md` with YAML front matter (`name`, `description`, `parent`, `children`) plus `agents/openai.yaml` runtime metadata. Use `references/` for supporting docs that are too detailed for the main skill.

Examples:

- `.ai/agents/orchestrator/AGENT.md`: default entrypoint for non-trivial work.
- `.ai/agents/backend/AGENT.md`: backend worker behavior and reporting rules.
- `.ai/skills/django/SKILL.md`: Django implementation patterns and references.

## Build, Test, and Development Commands

There is no application build or automated test suite configured in this repository. Useful local checks are:

- `rg --files .ai`: list canonical agent and skill files.
- `sed -n '1,120p' .ai/agents/<agent>/AGENT.md`: review an agent quickly.
- `sed -n '1,120p' .ai/skills/<skill>/SKILL.md`: review a skill quickly.
- `git status --short`: confirm only intended files changed.
- `python3 scripts/verify_agent_first_surface.py`: verify the public `.ai` agent hierarchy, skill packages, and reference paths.

When adding executable scripts or generated assets, document their commands in the related skill and update this guide if they become repository-wide.

## Coding Style & Naming Conventions

Write documentation in clear, direct Markdown. Keep `AGENT.md` and `SKILL.md` files action-oriented: explain when to use the agent or skill, what workflow to follow, and which references to load. Prefer lowercase kebab-case for directory names.

Use YAML front matter consistently:

```yaml
---
name: skill-name
description: Short trigger-oriented description.
---
```

Use two-space indentation in YAML. Keep examples small and specific to the workflow.

## AI Implementation Gate

Before backend implementation, inspect the target repository conventions and summarize the evidence before editing code. This gate applies to backend work that touches configuration, database access, dependency injection, services, repositories, error handling, testing, app startup, Celery, Django, FastAPI, or generic Python backend modules.

The convention report must cover:

- Configuration pattern: Pydantic Settings, Dynaconf, Django settings, environment variables, dataclasses, or another existing pattern.
- Database/session pattern: Django ORM, SQLAlchemy sync or async, session factory, engine lifecycle, FastAPI lifespan, migrations, or Django initialization.
- Dependency injection style: framework dependencies, explicit function parameters, service constructors, global clients, or existing provider modules.
- Service/repository boundaries: where business logic, persistence queries, and external I/O belong.
- Error handling style: exceptions, HTTP errors, result objects, logging, and failure translation.
- Testing style: test framework, fixture shape, naming, mocks/fakes, database setup, and validation commands.
- Naming and module organization: package layout, file naming, import style, and helper placement.

Existing project conventions override generic best practices, source-repo examples, and reusable skill examples. Do not introduce duplicate configuration, database, session, dependency-injection, service, repository, or testing abstractions when the target repository already has a pattern. If the convention is unclear, report the uncertainty and choose the smallest reversible change instead of silently inventing architecture.

## Mires Agent-First Architecture

Active Mires runtime discovery is agent-first and `.ai`-only. Public entrypoints are documented in `.ai/AGENTS.md` and `.ai/agents/**/AGENT.md`. Detailed implementation guidance lives under `references/` folders in `.ai/skills` and is loaded by the owning agent or workflow.

When adding a public agent, update `.ai/AGENTS.md`, `.ai/agents`, and `scripts/verify_agent_first_surface.py` in the same change. Keep agents behavior-focused and keep patterns, examples, checklists, and anti-patterns in skills. Do not add compatibility skill packages or public granular skill redirects when a reference can be owned by an existing agent or workflow.

## Testing Guidelines

For documentation-only changes, validate by reading the rendered Markdown and checking links to relative files. If an agent or skill references `references/`, `agents/`, `scripts/`, or `assets/`, verify those paths exist. For YAML files, use a parser or editor validation before committing.

## Commit & Pull Request Guidelines

This repository has no existing commit history, so no local convention is established yet. Use short imperative commit messages, for example `add django endpoint skill` or `update python testing reference`.

Pull requests should summarize changed skills, explain why the change is needed, and list manual validation performed. Include screenshots only for changes that affect rendered documentation or visual assets.

## Security & Configuration Tips

Do not commit secrets, personal tokens, API keys, or private environment values in `SKILL.md`, `agents/*.yaml`, examples, or references. Use placeholders like `OPENAI_API_KEY` when configuration is necessary.
