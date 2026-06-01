## Why

Mires has many useful implementation skills, but backend agents can still apply generic patterns before discovering the target repository's conventions. This change adds a convention-gated workflow so backend implementation starts from local evidence instead of assumptions.

## What Changes

- Add a project-conventions discovery workflow that must run before backend implementation.
- Add a backend orchestrator workflow that selects relevant skills only after convention discovery.
- Add a backend reviewer workflow and checklist that blocks configuration, database, dependency-injection, service-layer, error-handling, testing, and module-organization drift.
- Add a Python settings skill that explicitly prefers existing configuration systems such as Pydantic Settings, Dynaconf, Django settings, or existing environment handling over new abstractions.
- Add global repository guidance that makes existing project conventions higher priority than generic Mires examples.
- Keep the first implementation Codex-compatible while writing the new guidance in tool-agnostic Markdown that can later be adapted to OpenCode or other agent runtimes.

## Capabilities

### New Capabilities

- `convention-gated-ai-workflows`: Defines the required convention-discovery, backend orchestration, review-gate, and settings-pattern behavior for Mires AI-agent workflows.

### Modified Capabilities

- None.

## Impact

- Affected files include `AGENTS.md`, new or updated `.codex/skills/mires-*` skill packages, optional `agents/openai.yaml` entries for new workflow agents, and active documentation such as `docs/mires-skill-architecture.md`.
- Existing implementation skills remain usable, but backend work must pass through convention discovery before applying them.
- No application runtime code, package dependencies, public APIs, or installer commands are expected to change in the first implementation.
