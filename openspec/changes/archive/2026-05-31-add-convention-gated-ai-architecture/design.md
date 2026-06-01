## Context

Mires currently packages Codex skills under `.codex/skills/` with a useful router/leaf split. Workflow skills such as planner, reviewer, researcher, and tester already exist, and some have lightweight `agents/openai.yaml` entrypoints.

The main gap is that backend implementation can still start from a generic technical skill before the agent has proven which conventions the target repository already uses. Several backend skills also contain source-repo examples that are helpful references but can be misread as defaults for unrelated projects. The new architecture needs to make convention discovery mandatory before backend code changes while preserving the existing skill library.

## Goals / Non-Goals

**Goals:**
- Add a mandatory project-conventions discovery workflow before backend implementation.
- Add a backend orchestrator workflow that sequences convention discovery, relevant skill selection, implementation, validation, and review.
- Add a backend reviewer workflow that explicitly checks for implementation drift.
- Add a focused Python settings skill that prevents accidental introduction of new configuration patterns.
- Add global guidance that existing project conventions override generic examples.
- Keep content simple, Markdown-based, and adaptable to other agent runtimes later.

**Non-Goals:**
- Replace the existing `.codex/skills/` package layout in this first change.
- Reintroduce active OpenCode runtime assets or install targets.
- Build a generator that syncs `.ai/`, `.codex/`, and future runtime adapters.
- Rewrite every existing backend skill in one pass.
- Add external dependencies or change package installation behavior.

## Decisions

### Add workflow skills instead of embedding the gate into every leaf skill

Create dedicated workflow guidance for project-conventions discovery, backend orchestration, and backend review. This keeps leaf skills focused on implementation details and makes the pre-implementation gate reusable across FastAPI, Django, Celery, SQLAlchemy, testing, and generic Python work.

Alternative considered: update every backend leaf with a full convention-discovery checklist. That would duplicate rules across many files and increase drift.

### Add a Python settings leaf skill

Configuration drift is a concrete recurring failure mode, so settings deserve a narrow implementation skill. The skill should require agents to inspect existing settings modules, dependencies, and environment handling before adding fields or abstractions. It should explicitly forbid dataclass-based settings when the project already uses Pydantic Settings, Dynaconf, Django settings, or another established pattern.

Alternative considered: put settings guidance only in the backend orchestrator. That would help process but would not give implementation-level guidance when code touches configuration directly.

### Keep Codex as the first adapter and write content in portable Markdown

Implement the first version as Mires Codex skills and optional `agents/openai.yaml` entries because the current package and installer are Codex-only. Write the actual instructions without Codex-only concepts except where adapter metadata is required. This makes later migration to `.ai/` canonical files or another runtime possible without changing the behavior.

Alternative considered: introduce `.ai/` as the canonical source immediately. That would be more tool-agnostic but would conflict with the current Codex-only packaging direction and require generator or installer decisions that are not needed for the immediate behavior fix.

### Convert repo-specific source signals into examples over time

Do not block this change on rewriting every existing backend skill. Instead, add global and workflow-level rules stating that source-repo examples are non-authoritative unless they match the current target repository. Then update the highest-risk backend skills first, especially settings, FastAPI/Postgres connection setup, FastAPI app setup, Postgres patterns, Celery app setup, and service patterns.

Alternative considered: bulk-rewrite all backend skills in one change. That increases review risk and makes the first useful behavior improvement slower.

## Risks / Trade-offs

- Agents may skip the workflow skill if users invoke a leaf skill directly -> Mitigate by adding the convention gate to `AGENTS.md`, the Mires explorer/router, and backend workflow agent prompts.
- More process can slow small edits -> Mitigate by keeping the convention report short and evidence-focused.
- Tool-agnostic ambitions can reintroduce runtime complexity too early -> Mitigate by keeping Codex as the only active adapter in this change.
- Existing source-repo examples can still bias agents -> Mitigate by updating high-risk skills and making current-repo evidence higher priority than examples.

## Migration Plan

1. Add global convention-gate guidance to `AGENTS.md`.
2. Add new Mires workflow skills for project-conventions, backend-orchestrator, and backend-reviewer.
3. Add `agents/openai.yaml` entrypoints only where a dedicated role improves invocation.
4. Add the Python settings skill and include it in the relevant router maps.
5. Update high-risk backend skills to clarify that existing project conventions override examples.
6. Update architecture documentation to explain the difference between skills, workflow agents, standards, and checklists.
7. Validate with targeted file reads, path checks, and `git status --short`.

## Open Questions

- Whether `.ai/` should become the canonical source in a later change, with `.codex/skills/` generated from it.
- Whether package verification should eventually check that all router maps include the new convention-gated workflows.
