## Context

Mires currently exposes an agent-first public surface, but the repository layout still makes `.codex/skills` the active source of truth. Public agents, compatibility redirect skills, detailed references, and OpenAI agent metadata are all nested under the same runtime-specific tree. This makes the architecture harder to understand and keeps future non-Codex adapters coupled to Codex file paths.

The existing specs already require bounded public agent discovery, concise compatibility redirects, and Codex-only distribution. This change keeps the product and package interface stable while introducing a runtime-neutral canonical authoring layout:

- `.ai/agents/<agent-name>/` for public agent entrypoints and agent metadata.
- `.ai/skills/<skill-name>/` for reusable skills, compatibility redirects, and agent-owned references.
- `.codex/skills/<skill-name>/` as the Codex-compatible export or mirror consumed by current Codex tooling.

The canonical `.ai/agents` tree is hierarchical. Top-level agents coordinate work, and nested agents provide focused implementation or verification guidance:

```text
.ai/agents/
  mires-planner/
  mires-explorer/
  mires-tester/
    mires-tester-agent-browser/
    mires-tester-portless/
  mires-researcher/
  mires-backend/
    mires-python/
      mires-python-sqlalchemy/
      mires-python-aws/
      mires-python-tdd/
      mires-python-patterns/
      mires-python-class-based/
      mires-python-function-based/
      mires-python-fastapi/
        mires-python-fastapi-sqlalchemy/
        mires-python-fastapi-postgres/
        mires-python-fastapi-tdd/
        mires-python-fastapi-celery/
        mires-python-fastapi-celery-beat/
      mires-python-django/
        mires-python-django-models/
        mires-python-django-serializer/
        mires-python-django-apis/
        mires-python-django-apps/
        mires-python-django-tests/
        mires-python-django-celery/
        mires-python-django-celery-beat/
        mires-python-django-patterns/
        mires-python-django-tdd/
  mires-frontend/
    mires-react/
      mires-react-query/
      mires-react-hook-form/
      mires-zod/
```

## Goals / Non-Goals

**Goals:**

- Make `.ai/agents` and `.ai/skills` the canonical active repository layout.
- Create the requested `.ai/agents` hierarchy with top-level coordinating agents and nested domain subagents.
- Define baseline behavior for planner, explorer, tester, tester browser, tester portless, researcher, backend, Python, FastAPI, Django, frontend, React, React Query, React Hook Form, and Zod agents.
- Preserve the current public Mires agent allowlist and compatibility redirect behavior.
- Keep existing Codex users working through `.codex/skills`.
- Update documentation and verification so drift between `.ai` and `.codex` is detected.
- Keep the implementation reversible by moving content and validating paths before removing compatibility exports.

**Non-Goals:**

- Rename the `@macwdo/mires` package, `mires` CLI, or Mires skill IDs.
- Reintroduce OpenCode or a second active runtime install surface.
- Change the external package name or CLI command.
- Redesign the content of existing agent instructions or reference docs beyond path and ownership updates.

## Decisions

### Canonical layout

Use `.ai/agents` for agent entrypoints and nested subagents. Use `.ai/skills` for reusable skills, compatibility redirects, and reference material that is loaded by those agents.

Rationale: the user-requested layout separates role-level agent invocation from reusable skill/reference material while avoiding a Codex-specific source path. It also aligns with the current agent-first architecture without changing skill IDs.

Alternative considered: keep `.codex/skills` canonical and add `.ai` aliases. That would preserve the current shape but would not solve the mismatch between the architecture and the repository layout.

### Compatibility export

Keep `.codex/skills` as a generated or synchronized compatibility export until Codex can consume `.ai` directly.

Rationale: current runtime discovery and developer instructions still consume Codex skills from `.codex/skills`. Removing that tree in the same change would break current usage. Treating it as output preserves behavior while making `.ai` the source of truth.

Alternative considered: move everything directly and delete `.codex/skills`. That is simpler structurally but creates unnecessary runtime breakage.

### Agent hierarchy and ownership

Each agent directory contains a concise instruction file that explains when to use the agent, what subagents or skills it can call, and what evidence it must gather before acting. Nested agents inherit the domain context of their parent but remain directly addressable by their Mires identifier.

Rationale: the requested structure is a working routing tree, not only a storage layout. Keeping the routing rules in each node makes planner/explorer/tester/backend/frontend delegation explicit and reviewable.

Alternative considered: keep only top-level agents and store all detailed guidance under `.ai/skills`. That would reduce directory count but would not match the requested agent hierarchy or make domain subagent usage visible.

### Delegation behavior

`mires-planner` defines how each agent should be used and can assemble task plans across the hierarchy. `mires-explorer` calls relevant domain subagents to inspect repositories and identify errors. `mires-tester` validates behavior, invokes `mires-explorer` before or during test planning to surface issues, and delegates browser and portless checks to `mires-tester-agent-browser` and `mires-tester-portless`. `mires-researcher` uses MCP tools or WebSearch for current internet research and returns cited implementation references.

Rationale: these behaviors encode the user's requested collaboration flow. They also separate exploration, testing, and research from implementation agents.

Alternative considered: make tester and explorer independent. Requiring tester to call explorer gives verification work a bug-finding pass before test execution and fits the requested behavior.

### Verification

Update `scripts/verify_agent_first_surface.py` to validate `.ai` first, then validate `.codex/skills` as a compatibility export.

Rationale: verification should enforce the new source of truth and catch broken path moves, stale `.codex` documentation, missing agent metadata, redirect drift, and broad public-surface regressions.

Alternative considered: add a second script for `.ai`. A single script is preferable because this repository already has one authoritative agent-surface verification command.

## Risks / Trade-offs

- Path churn can break references -> mitigate by updating docs in the same change and extending verification to check referenced `.ai`, `.codex`, `docs`, and `scripts` paths.
- Generated or mirrored `.codex` assets can drift -> mitigate by either adding a deterministic sync script or verifying byte-for-byte/source-mapped parity for exported files.
- Contributors may edit `.codex/skills` directly -> mitigate with AGENTS.md guidance and verification failures when canonical `.ai` content does not match compatibility exports.
- The `.ai/agents` versus `.ai/skills` ownership boundary can become ambiguous -> mitigate by documenting which content belongs in each tree and requiring public agent list updates when a new agent is added.

## Migration Plan

1. Create `.ai/agents` and `.ai/skills` directories.
2. Move public agent entrypoint instructions and metadata into `.ai/agents/<agent-name>/`.
3. Move skill packages, compatibility redirects, and reference files into `.ai/skills/<skill-name>/`.
4. Create or update the Codex compatibility export under `.codex/skills`.
5. Update `AGENTS.md`, `.ai/skills/mires/SKILL.md`, and `docs/mires-agent-architecture.md` to describe `.ai` as canonical.
6. Update `scripts/verify_agent_first_surface.py` to validate the canonical layout and Codex export.
7. Run `python3 scripts/verify_agent_first_surface.py` and targeted path checks.

Rollback is to restore `.codex/skills` as the canonical tree and remove `.ai` references from docs and verification. Since no package name or external API changes are planned, rollback is limited to repository layout and docs.

## Open Questions

- Should `.codex/skills` be committed as a compatibility mirror, or should it be generated during package installation/build only?
- Should the sync/export logic live in the existing verification script or in a separate script invoked by verification?
