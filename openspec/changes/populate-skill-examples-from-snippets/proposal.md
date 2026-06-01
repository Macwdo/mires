## Why

The `.ai/skills` reference set preserves the right agent-first structure, but several backend-oriented references remain abstract while `.snippets/python` already contains concrete examples for the same patterns. This change makes the reference material more actionable by folding relevant snippet examples into the owning skill references without expanding the public skill surface.

## What Changes

- Add or enrich examples in `.ai/skills` reference docs using `.snippets/python` as source material where it clarifies existing guidance.
- Cover FastAPI app startup, async SQLAlchemy engine/session lifecycle, FastAPI dependencies, service boundaries, AWS client construction, Celery worker setup, Docker Compose local infrastructure, and Python project tooling examples.
- Keep examples in agent-owned references under `.ai/skills/**/references` rather than adding new public granular skills or compatibility redirects.
- Remove the temporary `.snippets` source tree after useful examples have been migrated into canonical skill references.
- Add validation expectations so referenced snippet-derived examples stay reachable and documentation paths remain accurate.

## Capabilities

### New Capabilities

- `skill-reference-examples`: Defines how canonical `.ai/skills` reference packages include concrete implementation examples sourced from local snippets while preserving agent-first routing.

### Modified Capabilities

- `mires-agent-context-routing`: Clarifies that selected granular guidance may include concrete examples inside agent-owned references without becoming public routing entries.
- `mires-namespace-distribution`: Clarifies that `.ai` remains the only active runtime surface while local snippet material may be used as authoring input for canonical `.ai/skills` references.

## Impact

- Affected files include `.ai/skills/backend/references/*.md`, `.ai/skills/fastapi/references/*.md`, `.ai/skills/celery/references/*.md`, `.ai/skills/python/references/*.md`, and related verification/documentation if reference paths change.
- `.snippets/python/**` is treated as temporary source material for examples, not as a new runtime discovery surface, and should be removed once migrated.
- No runtime API, CLI, package dependency, or generated application behavior changes are expected.
