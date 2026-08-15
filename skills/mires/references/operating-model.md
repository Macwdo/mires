# Operating Model

## Classify

- Handle a simple, low-risk, single-surface task directly.
- Treat meaningful ambiguity, cross-cutting behavior, or validation risk as medium.
- Treat broad features, multiple repositories, architecture choices, or external unknowns as complex.

## Investigate

- Map ownership, entrypoints, dependencies, nearby examples, and validation commands before editing.
- For backend work, record configuration, database/session, dependency injection, service/repository, error, testing, naming, and module conventions.
- For frontend work, record framework, routing, server/client boundaries, component composition, state ownership, forms, contracts, accessibility, and test conventions.
- Verify current external behavior from primary sources when it can drift.

## Delegate

- Use specialist subagents for independent investigation when available and when they materially improve confidence.
- Keep investigation agents read-only.
- Merge findings into one brief before implementation.
- Select exactly one implementation owner so concurrent edits do not collide.
- Add explicit test and review passes for implementation work when the risk justifies them.

## Implement

- Preserve explicit constraints and unrelated state.
- Prefer the smallest reversible change when conventions are unclear.
- Keep behavior in the owning module and avoid cross-layer shortcuts.
- Do not broaden authority from implementation into commits, pushes, deployments, data resets, or external communication.

## Verify

- Run focused tests first, then repository-wide checks appropriate to the change.
- Check formatting and `git diff --check` when files changed.
- Inspect the final diff and repository status.
- Report what passed, what could not be run, and the remaining risk.
