---
name: macwdo-explorer
description: "Explore Macwdo skill families and select the correct granular leaf skill. Use when a user or subagent needs to discover which Macwdo skill applies to internet-backed research, generic Python, Django, LangGraph, React, Next.js, local app testing, FastAPI, Postgres, Alembic, Celery, Docker Compose, service-layer, or DevEx work."
---

# Macwdo Explorer

Use this router to choose a specific Macwdo leaf skill. Load the narrowest matching skill before implementation.

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

### Django

- `macwdo-python-django-explorer` at `.codex/skills/macwdo-python-django-explorer/SKILL.md`
- `macwdo-python-django-models-base-classes` at `.codex/skills/macwdo-python-django-models-base-classes/SKILL.md`
- `macwdo-python-django-models-fields-relationships` at `.codex/skills/macwdo-python-django-models-fields-relationships/SKILL.md`
- `macwdo-python-django-models-str-timestamps` at `.codex/skills/macwdo-python-django-models-str-timestamps/SKILL.md`
- `macwdo-python-django-models-appconfig-admin` at `.codex/skills/macwdo-python-django-models-appconfig-admin/SKILL.md`
- `macwdo-python-django-models-special-fields` at `.codex/skills/macwdo-python-django-models-special-fields/SKILL.md`
- `macwdo-python-django-models-migrations` at `.codex/skills/macwdo-python-django-models-migrations/SKILL.md`
- `macwdo-python-django-services-functions` at `.codex/skills/macwdo-python-django-services-functions/SKILL.md`
- `macwdo-python-django-services-transactions` at `.codex/skills/macwdo-python-django-services-transactions/SKILL.md`
- `macwdo-python-django-services-flow-services` at `.codex/skills/macwdo-python-django-services-flow-services/SKILL.md`
- `macwdo-python-django-services-dependencies` at `.codex/skills/macwdo-python-django-services-dependencies/SKILL.md`
- `macwdo-python-django-services-exceptions` at `.codex/skills/macwdo-python-django-services-exceptions/SKILL.md`
- `macwdo-python-django-services-boundaries` at `.codex/skills/macwdo-python-django-services-boundaries/SKILL.md`
- `macwdo-python-django-selectors-detail` at `.codex/skills/macwdo-python-django-selectors-detail/SKILL.md`
- `macwdo-python-django-selectors-cached` at `.codex/skills/macwdo-python-django-selectors-cached/SKILL.md`
- `macwdo-python-django-selectors-list` at `.codex/skills/macwdo-python-django-selectors-list/SKILL.md`
- `macwdo-python-django-selectors-optimization` at `.codex/skills/macwdo-python-django-selectors-optimization/SKILL.md`
- `macwdo-python-django-selectors-boundaries` at `.codex/skills/macwdo-python-django-selectors-boundaries/SKILL.md`
- `macwdo-python-django-serializers-input` at `.codex/skills/macwdo-python-django-serializers-input/SKILL.md`
- `macwdo-python-django-serializers-output` at `.codex/skills/macwdo-python-django-serializers-output/SKILL.md`
- `macwdo-python-django-serializers-action-aware` at `.codex/skills/macwdo-python-django-serializers-action-aware/SKILL.md`
- `macwdo-python-django-serializers-advanced-functions` at `.codex/skills/macwdo-python-django-serializers-advanced-functions/SKILL.md`
- `macwdo-python-django-serializers-boundaries` at `.codex/skills/macwdo-python-django-serializers-boundaries/SKILL.md`
- `macwdo-python-django-endpoints-api-view` at `.codex/skills/macwdo-python-django-endpoints-api-view/SKILL.md`
- `macwdo-python-django-endpoints-viewset-actions` at `.codex/skills/macwdo-python-django-endpoints-viewset-actions/SKILL.md`
- `macwdo-python-django-endpoints-crud-viewsets` at `.codex/skills/macwdo-python-django-endpoints-crud-viewsets/SKILL.md`
- `macwdo-python-django-endpoints-service-first-crud` at `.codex/skills/macwdo-python-django-endpoints-service-first-crud/SKILL.md`
- `macwdo-python-django-endpoints-routing` at `.codex/skills/macwdo-python-django-endpoints-routing/SKILL.md`
- `macwdo-python-django-endpoints-responses` at `.codex/skills/macwdo-python-django-endpoints-responses/SKILL.md`
- `macwdo-python-django-tests-tdd-workflow` at `.codex/skills/macwdo-python-django-tests-tdd-workflow/SKILL.md`
- `macwdo-python-django-tests-naming-structure` at `.codex/skills/macwdo-python-django-tests-naming-structure/SKILL.md`
- `macwdo-python-django-tests-authenticated-api` at `.codex/skills/macwdo-python-django-tests-authenticated-api/SKILL.md`
- `macwdo-python-django-tests-unauthenticated-api` at `.codex/skills/macwdo-python-django-tests-unauthenticated-api/SKILL.md`
- `macwdo-python-django-tests-helpers-fixtures` at `.codex/skills/macwdo-python-django-tests-helpers-fixtures/SKILL.md`
- `macwdo-python-django-tests-drf-rules` at `.codex/skills/macwdo-python-django-tests-drf-rules/SKILL.md`
- `macwdo-python-django-tests-mocking-external-services` at `.codex/skills/macwdo-python-django-tests-mocking-external-services/SKILL.md`
- `macwdo-python-django-tests-pagination` at `.codex/skills/macwdo-python-django-tests-pagination/SKILL.md`
- `macwdo-python-django-tests-forbidden-patterns` at `.codex/skills/macwdo-python-django-tests-forbidden-patterns/SKILL.md`
- `macwdo-python-django-project-bootstrap` at `.codex/skills/macwdo-python-django-project-bootstrap/SKILL.md`

### LangGraph

- `macwdo-python-langgraph-explorer` at `.codex/skills/macwdo-python-langgraph-explorer/SKILL.md`
- `macwdo-python-langgraph-state` at `.codex/skills/macwdo-python-langgraph-state/SKILL.md`
- `macwdo-python-langgraph-services` at `.codex/skills/macwdo-python-langgraph-services/SKILL.md`
- `macwdo-python-langgraph-node-factory` at `.codex/skills/macwdo-python-langgraph-node-factory/SKILL.md`
- `macwdo-python-langgraph-graph-assembly` at `.codex/skills/macwdo-python-langgraph-graph-assembly/SKILL.md`
- `macwdo-python-langgraph-llm-nodes` at `.codex/skills/macwdo-python-langgraph-llm-nodes/SKILL.md`
- `macwdo-python-langgraph-service-node-pattern` at `.codex/skills/macwdo-python-langgraph-service-node-pattern/SKILL.md`

### React

- `macwdo-typescript-react-explorer` at `.codex/skills/macwdo-typescript-react-explorer/SKILL.md`
- `macwdo-typescript-react-state-decision-matrix` at `.codex/skills/macwdo-typescript-react-state-decision-matrix/SKILL.md`
- `macwdo-typescript-react-forms` at `.codex/skills/macwdo-typescript-react-forms/SKILL.md`
- `macwdo-typescript-react-server-state` at `.codex/skills/macwdo-typescript-react-server-state/SKILL.md`
- `macwdo-typescript-react-client-state` at `.codex/skills/macwdo-typescript-react-client-state/SKILL.md`
- `macwdo-typescript-react-anti-patterns` at `.codex/skills/macwdo-typescript-react-anti-patterns/SKILL.md`

### Next.js

- `macwdo-typescript-next-explorer` at `.codex/skills/macwdo-typescript-next-explorer/SKILL.md`
- `macwdo-typescript-next-server-first` at `.codex/skills/macwdo-typescript-next-server-first/SKILL.md`
- `macwdo-typescript-next-project-bootstrap` at `.codex/skills/macwdo-typescript-next-project-bootstrap/SKILL.md`
- `macwdo-typescript-next-react-query-setup` at `.codex/skills/macwdo-typescript-next-react-query-setup/SKILL.md`
- `macwdo-typescript-next-axios-setup` at `.codex/skills/macwdo-typescript-next-axios-setup/SKILL.md`
- `macwdo-typescript-next-zustand-setup` at `.codex/skills/macwdo-typescript-next-zustand-setup/SKILL.md`
- `macwdo-typescript-next-form-setup` at `.codex/skills/macwdo-typescript-next-form-setup/SKILL.md`

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

- Prefer the most specific leaf skill over a router.
- For cross-cutting tasks, load each relevant leaf.
- Keep FastAPI, Postgres, Celery, Docker, and DevEx skills unchanged and compose them with the new leaves when needed.
