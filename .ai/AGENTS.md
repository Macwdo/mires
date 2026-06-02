## Mires Runtime Routing

Use the orchestrator as the default entrypoint for non-trivial work.

- For any non-trivial engineering task, route through `.ai/agents/orchestrator/AGENT.md` first.
- The user should not need to manually request subagents.
- Broad implementation requests such as "implement a new API", "build a feature", or "add product support" are non-trivial by default and must be orchestrated.
- The orchestrator should delegate to every specialist that can materially improve quality, even when this uses more tokens.
- Simple tasks can be handled directly when no specialist investigation is needed.
- Medium and complex tasks must be delegated to specialist agents before implementation.
- Most specialist agents should inspect and report before implementation starts.
- Only one final implementation agent should edit files.
- Tester and reviewer should be involved for implementation work unless the change is clearly documentation-only or validation is impossible.
- Prefer project conventions over generic advice.
- Always inspect existing code patterns before proposing new patterns.

## Agents

- `orchestrator`: default coordinator for medium and complex work.
- `explorer`: maps files, entrypoints, dependencies, and existing patterns.
- `backend`: handles Python backend implementation after investigation is complete.
- `frontend`: handles React and Next.js implementation after investigation is complete.
- `tester`: defines and runs unit, integration, and end-to-end verification.
- `reviewer`: reviews correctness, risk, security, maintainability, and test coverage.
- `planner`: turns ambiguous requests into decision-ready implementation plans.
- `researcher`: gathers current external facts from official docs and source repositories.

## Reference Skills

Skills are owner-loaded reference packages, not a public routing catalog. Agents decide when to load them, and granular legacy skill names must route through the owning agent or workflow instead of through compatibility redirects.

- Backend stack: `backend`, `python`, `django`, `fastapi`, `sqlalchemy`, `postgres`, `celery`, `langgraph`
- Frontend stack: `frontend`, `react`, `next`, `typescript`
- Cross-cutting: `testing`, `review`, `project-conventions`, `openspec`

## Compatibility Tooling

The `.ai/agents` and `.ai/skills` trees are runtime-agnostic source assets. Python compatibility tooling under `src/compatibility` reads those assets and applies runtime-specific adapter checks, starting with Codex. Run `python3 src/main.py --target codex` from the repository root to validate Codex compatibility.
