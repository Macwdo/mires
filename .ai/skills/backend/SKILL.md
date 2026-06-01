---
name: backend
description: Backend architecture and service-layer rules for Python applications after local conventions are inspected.
---

# Backend

## When To Use

Use for backend architecture, service-layer boundaries, settings usage, Docker Compose setup, and backend integration decisions that are broader than one framework.

## Core Rules

- Inspect repository conventions before proposing abstractions.
- Keep business logic out of framework entrypoints.
- Reuse the existing settings, dependency, and service boundaries.
- Prefer small reversible changes when the local pattern is unclear.

## Preferred Patterns

- Thin routes, views, handlers, and tasks.
- Explicit service or orchestration layers.
- Settings-driven construction.
- Focused validation matched to the touched boundary.

## Anti-Patterns

- Inventing a new backend architecture without local evidence.
- Mixing business logic into controllers, routes, or tasks.
- Adding duplicate settings, client factories, or session management layers.

## Checklist

- Inspect project conventions first.
- Identify the existing service and dependency boundaries.
- Pick only the backend-adjacent references that match the repo.
- Validate the touched backend path.

## References Index

- `references/service-patterns.md`
- `references/settings.md`
- `references/docker-compose-patterns.md`
- `references/docker-compose-local-infra.md`
