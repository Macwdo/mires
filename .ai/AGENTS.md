## Mires Runtime Routing

Use the orchestrator as the default entrypoint for non-trivial work.

- For any non-trivial engineering task, route through `.ai/agents/orchestrator/AGENT.md` first.
- The user should not need to manually request subagents.
- The orchestrator decides whether delegation is needed.
- Simple tasks can be handled directly when no specialist investigation is needed.
- Medium and complex tasks should be delegated to specialist agents.
- Most specialist agents should inspect and report before implementation starts.
- Only one final implementation agent should edit files.
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
