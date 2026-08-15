# Personal Preferences

## Outcome

- Pursue the requested end state through the real code, contract, and runtime path.
- Treat exact product and UI corrections as acceptance criteria, including scope, breakpoint, ownership, persistence, and navigation behavior.
- Prefer a complete working handoff with concrete verification over a speculative recommendation.

## Repository Discipline

- Read repository instructions and inspect existing patterns before proposing architecture.
- Respect child-repository and worktree boundaries.
- Preserve unrelated dirty state and re-check status after interruptions.
- Extend the repository's configuration, database, dependency, service, state, error, and test patterns instead of creating parallel abstractions.
- Keep changes focused. Do not commit or push unless requested.

## Implementation Taste

- Prefer simple services and explicit boundaries over custom orchestration.
- Keep domain modules independent from application entrypoints.
- Pair model, contract, or business-flow changes with representative fixtures and tests when the project uses them.
- Preserve existing desktop or routed surfaces when the request adds a mobile, dialog, drawer, or summary surface.
- Add loading, success, empty, retry, and error states to user-facing workflows when relevant.

## Communication

- Lead with the outcome and material decisions.
- Explain assumptions, evidence, validation, and residual risk concisely.
- Ask only when a missing decision would materially change the result or require new authority.
