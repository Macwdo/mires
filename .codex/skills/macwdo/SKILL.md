---
name: macwdo
description: "Macwdo principal skill namespace. Use when the user asks for Macwdo skills, Macwdo conventions, internet-backed research, or help discovering granular Python, Django, LangGraph, React, Next.js, local app testing, FastAPI, Postgres, Celery, Docker Compose, service-layer, and DevEx skills."
---

# Macwdo

This is Macwdo's principal namespace for local repo skills. Use it as the entrypoint when a request names Macwdo skills or asks broadly for Macwdo conventions. For implementation work, load the narrowest matching leaf skill first.

## Skill Map

### Planning

- `macwdo-planner` at `.codex/skills/macwdo-planner/SKILL.md`

### Research

- `macwdo-researcher` at `.codex/skills/macwdo-researcher/SKILL.md`

### Review

- `macwdo-reviewer` at `.codex/skills/macwdo-reviewer/SKILL.md`

### Generic Python

- `macwdo-python-functions` at `.codex/skills/macwdo-python-functions/SKILL.md`
- `macwdo-python-typing-signatures` at `.codex/skills/macwdo-python-typing-signatures/SKILL.md`
- `macwdo-python-boundaries-dependencies` at `.codex/skills/macwdo-python-boundaries-dependencies/SKILL.md`
- `macwdo-python-state-mutation` at `.codex/skills/macwdo-python-state-mutation/SKILL.md`
- `macwdo-python-errors` at `.codex/skills/macwdo-python-errors/SKILL.md`
- `macwdo-python-module-shape` at `.codex/skills/macwdo-python-module-shape/SKILL.md`
- `macwdo-python-tests-workflow` at `.codex/skills/macwdo-python-tests-workflow/SKILL.md`
- `macwdo-python-tests-helpers` at `.codex/skills/macwdo-python-tests-helpers/SKILL.md`
- `macwdo-python-validation` at `.codex/skills/macwdo-python-validation/SKILL.md`

### Django Router

- `macwdo-python-django-explorer` at `.codex/skills/macwdo-python-django-explorer/SKILL.md`

### LangGraph Router

- `macwdo-python-langgraph-explorer` at `.codex/skills/macwdo-python-langgraph-explorer/SKILL.md`

### React Router

- `macwdo-typescript-react-explorer` at `.codex/skills/macwdo-typescript-react-explorer/SKILL.md`

### Next Router

- `macwdo-typescript-next-explorer` at `.codex/skills/macwdo-typescript-next-explorer/SKILL.md`

### Agent Testing

- `macwdo-tester` at `.codex/skills/macwdo-tester/SKILL.md`

### FastAPI, Postgres, Celery, Docker, DevEx

- `macwdo-python-fastapi-patterns` at `.codex/skills/macwdo-python-fastapi-patterns/SKILL.md`
- `macwdo-python-fastapi-app-setup` at `.codex/skills/macwdo-python-fastapi-app-setup/SKILL.md`
- `macwdo-python-fastapi-postgres-connection-setup` at `.codex/skills/macwdo-python-fastapi-postgres-connection-setup/SKILL.md`
- `macwdo-python-fastapi-celery-integration` at `.codex/skills/macwdo-python-fastapi-celery-integration/SKILL.md`
- `macwdo-python-postgres-patterns` at `.codex/skills/macwdo-python-postgres-patterns/SKILL.md`
- `macwdo-python-postgres-alembic-patterns` at `.codex/skills/macwdo-python-postgres-alembic-patterns/SKILL.md`
- `macwdo-python-service-patterns` at `.codex/skills/macwdo-python-service-patterns/SKILL.md`
- `macwdo-python-celery-app-setup` at `.codex/skills/macwdo-python-celery-app-setup/SKILL.md`
- `macwdo-python-celery-testing` at `.codex/skills/macwdo-python-celery-testing/SKILL.md`
- `macwdo-python-celery-live-worker-testing` at `.codex/skills/macwdo-python-celery-live-worker-testing/SKILL.md`
- `macwdo-python-docker-compose-patterns` at `.codex/skills/macwdo-python-docker-compose-patterns/SKILL.md`
- `macwdo-python-docker-compose-local-infra` at `.codex/skills/macwdo-python-docker-compose-local-infra/SKILL.md`
- `macwdo-python-devex-patterns` at `.codex/skills/macwdo-python-devex-patterns/SKILL.md`

## Selection Rules

- Do not treat this as an umbrella implementation guide.
- Choose and load the narrowest matching leaf skill before changing code or tests.
- Use explorer skills when the right leaf is not obvious.
