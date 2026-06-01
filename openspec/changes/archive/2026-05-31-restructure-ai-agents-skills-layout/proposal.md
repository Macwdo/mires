## Why

Mires currently stores all active runtime guidance under `.codex/skills`, even though the product model is agent-first and needs a runtime-neutral source layout. Moving the canonical authoring surface to `.ai/agents` and `.ai/skills` makes the repository structure match the architecture while preserving Codex compatibility.

## What Changes

- **BREAKING**: Treat `.ai/agents` and `.ai/skills` as the canonical active source layout for Mires agent and skill assets.
- Move public Mires agent entrypoints into `.ai/agents/<agent-name>/` with their agent metadata, usage instructions, and delegation rules.
- Create the requested `.ai/agents` hierarchy:
  - `mires-planner`
  - `mires-explorer`
  - `mires-tester`
    - `mires-tester-agent-browser`
    - `mires-tester-portless`
  - `mires-researcher`
  - `mires-backend`
    - `mires-python`
      - `mires-python-sqlalchemy`
      - `mires-python-aws`
      - `mires-python-tdd`
      - `mires-python-patterns`
      - `mires-python-class-based`
      - `mires-python-function-based`
      - `mires-python-fastapi`
        - `mires-python-fastapi-sqlalchemy`
        - `mires-python-fastapi-postgres`
        - `mires-python-fastapi-tdd`
        - `mires-python-fastapi-celery`
        - `mires-python-fastapi-celery-beat`
      - `mires-python-django`
        - `mires-python-django-models`
        - `mires-python-django-serializer`
        - `mires-python-django-apis`
        - `mires-python-django-apps`
        - `mires-python-django-tests`
        - `mires-python-django-celery`
        - `mires-python-django-celery-beat`
        - `mires-python-django-patterns`
        - `mires-python-django-tdd`
  - `mires-frontend`
    - `mires-react`
      - `mires-react-query`
      - `mires-react-hook-form`
      - `mires-zod`
- Move reusable skills, compatibility redirects, and agent-owned reference material into `.ai/skills/<skill-name>/`.
- Define delegation behavior: `mires-explorer` calls domain subagents to explore and identify errors; `mires-tester` validates working behavior and calls `mires-explorer` to check for bugs or issues; `mires-researcher` uses MCPs or WebSearch for internet implementation research and references.
- Preserve Codex runtime compatibility by keeping `.codex/skills` as an install/generated mirror or compatibility export, not the primary authoring location.
- Update documentation, verification, and contributor guidance to reference the `.ai` layout and prevent drift between canonical `.ai` assets and Codex-compatible assets.

## Capabilities

### New Capabilities
- `ai-agent-skill-layout`: Defines the canonical `.ai/agents` and `.ai/skills` repository layout, ownership rules, and compatibility export expectations.

### Modified Capabilities
- `mires-agent-context-routing`: Public agent discovery and granular context loading must resolve from the canonical `.ai` layout while preserving the existing bounded public surface.
- `mires-namespace-distribution`: Distribution and verification must package Codex-compatible assets from the canonical `.ai` layout and stop treating `.codex/skills` as the source of truth.

## Impact

- Affected source layout: `.ai/agents/**`, `.ai/skills/**`, and compatibility output under `.codex/skills/**`.
- Affected docs and governance: `AGENTS.md`, `docs/mires-agent-architecture.md`, and OpenSpec capability docs.
- Affected verification: `scripts/verify_agent_first_surface.py` must validate canonical `.ai` assets, expected compatibility exports, public agent allowlists, redirect stubs, and referenced paths.
- No external API or package name changes are intended; the `@macwdo/mires` package and `mires` CLI remain the distribution interface.
