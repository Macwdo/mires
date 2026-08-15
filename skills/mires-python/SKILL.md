---
name: mires-python
description: Apply Macwdo's Python backend standards across plain modules, services, FastAPI apps, SQLAlchemy and Postgres data access, Celery workers, and LangGraph workflows. Use for Python implementation, refactoring, or review when the work is not Django-specific.
---

# Mires Python

Use this skill for Python work outside Django. Inspect the target repository first: its existing conventions outrank everything here. Load only the rule document for the boundary you are touching.

## Start With The Repository

1. Read the target module, its siblings, and the nearby tests before changing anything.
2. Record the configuration, session, dependency-injection, service, error, and testing patterns already in use.
3. Apply the rules below only where the repository has not already established a stronger convention.
4. Run the repository's own checks when you are done.

## Route By Boundary

Each rule document states when to use it, the core rules, preferred patterns, anti-patterns, and a checklist. Read the one that matches the boundary, then follow its reference index for detail.

- Generic modules, typing, boundaries, errors, and tests: `references/python/rules.md`
- Service layers, settings, and local infrastructure: `references/backend/rules.md`
- FastAPI apps, routes, dependencies, and schemas: `references/fastapi/rules.md`
- SQLAlchemy sessions, models, and query boundaries: `references/sqlalchemy/rules.md`
- Postgres schema and migration work: `references/postgres/rules.md`
- Celery tasks, workers, queues, and worker tests: `references/celery/rules.md`
- LangGraph state, nodes, and graph assembly: `references/langgraph/rules.md`

For Django or DRF work, use `$mires-django` instead. For frontend contracts consumed by a Python API, use `$mires-typescript`.

## Decision Rules

- Prefer typed functions and small modules over large stateful classes.
- Keep domain logic in plain Python; keep framework glue, HTTP adapters, and graph wiring thin.
- Pass dependencies in from the edge instead of constructing them deep inside core logic.
- Prefer explicit inputs and return values over hidden mutation.
- Do not introduce repository or use-case layers unless the target repository already owns them.

## References

- `references/python/rules.md`: generic Python module, typing, boundary, error, and test rules
- `references/backend/rules.md`: backend architecture and service-layer rules
- `references/fastapi/rules.md`: FastAPI app setup, routes, dependencies, and schemas
- `references/sqlalchemy/rules.md`: SQLAlchemy session, model, and query boundaries
- `references/postgres/rules.md`: Postgres and migration guidance
- `references/celery/rules.md`: Celery task, worker, and queue guidance
- `references/langgraph/rules.md`: LangGraph typed state, service-backed nodes, and graph assembly
