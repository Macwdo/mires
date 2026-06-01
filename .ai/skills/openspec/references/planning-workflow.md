---
name: implementation-planning-workflow
description: "Plan implementation work using the current `.ai` agents and skills. Use when the user asks for an implementation plan, feature plan, or architecture plan."
---

# Mires Planner

Use this reference to produce implementation plans grounded in the repository and the relevant `.ai` pattern skills. This is a planning reference, not an implementation guide.

## Workflow

1. Identify the user's goal, success criteria, scope, and likely implementation surface from the request.
2. Inspect the repository before asking questions. Prefer `rg`, `rg --files`, targeted file reads, and existing configs.
3. Start with `orchestrator` when the relevant specialist agent is not obvious.
4. Use `researcher` to verify external libraries, APIs, setup commands, architecture options, and current behavior before finalizing the plan.
5. Select the specialist agent first, then name the narrow skills and references it should use.
6. Use the selected skill guidance and cited research to create a decision-complete plan that another engineer or agent can execute.
7. Ask the user only for product or tradeoff decisions that cannot be discovered from the repo or verified references.

## Skill Selection

For common requests, start with these routing defaults:

- FastAPI endpoint or route work: `backend` plus `fastapi`.
- FastAPI with Postgres: `backend` plus `fastapi` and `postgres`.
- FastAPI with Celery: `backend` plus `fastapi` and `celery`.
- Generic Python services: `backend` plus `backend` and `python` skills.
- Django work: `backend` plus `django`.
- LangGraph work: `backend` plus `langgraph`.
- React or Next.js work: `frontend` plus `react`, `next`, or `typescript`.
- Test planning: `tester` plus `testing`.

Do not load unrelated leaf skills just to be exhaustive. A good plan names the skills that affect implementation decisions and omits the rest.

## Planning Output

Include these sections when they help the request:

1. Goal and success criteria.
2. Selected Mires skills and why each one applies.
3. Current repo signals that shape the plan.
4. Implementation steps grouped by subsystem or behavior.
5. Public interfaces, schemas, routes, types, or commands that will change.
6. Edge cases, error handling, and compatibility notes.
7. Test and validation plan.
8. Assumptions and defaults chosen.

Keep the plan concrete enough that implementation does not require additional architecture or skill-routing decisions.

## Standards

- Treat selected agent and skill references as reusable guidance, with target-repository conventions taking priority.
- Prefer existing repo patterns over new abstractions.
- Keep plans scoped to the requested behavior and the affected ownership boundaries.
- Do not edit code, apply patches, or run mutating commands while planning unless the user explicitly switches from planning to implementation.
- If the user asks for OpenSpec planning, include the relevant proposal, design, specs, and tasks shape in the plan.
