# `.ai` Migration Summary

## What Changed

- Replaced the old `mires-*` public agent surface with a smaller worker-oriented set:
  - `orchestrator`
  - `explorer`
  - `backend`
  - `frontend`
  - `tester`
  - `reviewer`
  - `planner`
  - `researcher`
- Added `.ai/AGENTS.md` as the runtime routing guide.
- Made the orchestrator the default entrypoint for non-trivial work.

## What Moved

- Old top-level agents were renamed into simpler folders under `.ai/agents/`.
- Nested backend, frontend, and tester subagents were removed from the public surface.
- Detailed framework guidance moved into simpler skill folders:
  - `django`
  - `fastapi`
  - `langgraph`
  - `react`
  - `next`
  - `testing`
  - `project-conventions`
- Shared backend references were split into:
  - `backend`
  - `python`
  - `postgres`
  - `celery`
- OpenSpec workflow content was merged under `.ai/skills/openspec/references/`.

## What Merged

- Backend orchestration guidance moved into `skills/backend` and contributed references to `skills/python`, `skills/postgres`, and `skills/celery`.
- Review guidance moved into `skills/review`.
- OpenSpec action guidance and planning workflow guidance were consolidated under `skills/openspec`.
- Project-convention guidance stopped being a public agent and now lives as `skills/project-conventions`.

## Current Compatibility Policy

- Detailed reference files were preserved rather than rewritten into thin summaries.
- `langgraph` was kept as a backend-related reference package.
- Existing reference filenames were mostly preserved to avoid unnecessary churn, but old granular skill IDs are not active public routes.
- Compatibility redirects are intentionally not retained when the guidance has an owning `.ai/skills/<domain>/references/` file.

## Ambiguous Files For Manual Review

- Long-form OpenSpec references now live under `skills/openspec/references/`; if you want them shorter or split differently, that is a follow-up cleanup.
- Some reference filenames still carry the older `mires-*` prefix even though the public surface is agent-first.

## How To Test The New Routing

1. Read `.ai/AGENTS.md` and confirm it routes non-trivial tasks to `orchestrator`.
2. Read `.ai/agents/orchestrator/AGENT.md` and verify delegation plus single-implementation-agent rules.
3. Run `python3 scripts/verify_agent_first_surface.py`.
4. Check `rg --files .ai` and confirm the public folders are simplified.
5. Check that old granular skill names route through the owning agent or workflow instead of compatibility redirects.

## Example Prompts

- `Refactor this Django endpoint to use a service layer and add tests.`
- `Find performance problems in this FastAPI route and propose a fix.`
- `Implement Celery for this long-running task, but first inspect the existing patterns.`
- `Review this PR for backend architecture, tests, and risky patterns.`
- `Explore this repo and tell me where the authentication flow lives.`
