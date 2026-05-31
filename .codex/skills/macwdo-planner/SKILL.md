---
name: macwdo-planner
description: "Plan implementation work using Macwdo conventions. Use when the user asks for an implementation plan, feature plan, architecture plan, or guidance on which Macwdo skills should be loaded before building Python, Django, FastAPI, LangGraph, React, Next.js, Postgres, Celery, Docker Compose, agent-testing, service-layer, or DevEx work."
---

# Macwdo Planner

Use this skill to produce implementation plans that are grounded in the repository and the relevant Macwdo pattern skills. This is a planning router, not an implementation guide.

## Workflow

1. Identify the user's goal, success criteria, scope, and likely implementation surface from the request.
2. Inspect the repository before asking questions. Prefer `rg`, `rg --files`, targeted file reads, and existing configs.
3. Load `macwdo-explorer` first when the relevant pattern family is not obvious.
4. Use `macwdo-researcher` to verify external libraries, APIs, setup commands, architecture options, and current behavior before finalizing the plan.
5. Select and load the narrowest relevant Macwdo leaf skills before planning implementation details.
6. Use the selected skill guidance and cited research to create a decision-complete plan that another engineer or agent can execute.
7. Ask the user only for product or tradeoff decisions that cannot be discovered from the repo or verified references.

## Skill Selection

For common requests, start with these routing defaults:

- FastAPI endpoint or route work: `macwdo-python-fastapi-patterns`.
- FastAPI app entrypoint, dependencies, schemas, or setup: `macwdo-python-fastapi-app-setup`.
- FastAPI with Postgres: add `macwdo-python-fastapi-postgres-connection-setup`, `macwdo-python-postgres-patterns`, or `macwdo-python-postgres-alembic-patterns` as needed.
- FastAPI with Celery: add `macwdo-python-fastapi-celery-integration` and the relevant Celery setup/testing skills.
- Generic Python services: use function, typing, boundary, validation, error, state-mutation, module-shape, and test skills that match the touched code.
- Django, LangGraph, React, Next.js, and agent-testing work: load the matching family explorer first, then the relevant leaf skills.

Do not load unrelated leaf skills just to be exhaustive. A good plan names the skills that affect implementation decisions and omits the rest.

## Planning Output

Include these sections when they help the request:

1. Goal and success criteria.
2. Selected Macwdo skills and why each one applies.
3. Current repo signals that shape the plan.
4. Implementation steps grouped by subsystem or behavior.
5. Public interfaces, schemas, routes, types, or commands that will change.
6. Edge cases, error handling, and compatibility notes.
7. Test and validation plan.
8. Assumptions and defaults chosen.

Keep the plan concrete enough that implementation does not require additional architecture or skill-routing decisions.

## Standards

- Treat Macwdo leaf skills as the source of truth for local conventions.
- Prefer existing repo patterns over new abstractions.
- Keep plans scoped to the requested behavior and the affected ownership boundaries.
- Do not edit code, apply patches, or run mutating commands while planning unless the user explicitly switches from planning to implementation.
- If the user asks for OpenSpec planning, include the relevant proposal, design, specs, and tasks shape in the plan.
