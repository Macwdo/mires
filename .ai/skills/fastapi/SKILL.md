---
name: fastapi
description: FastAPI patterns for app setup, routes, dependencies, schemas, database access, and worker integration.
---

# FastAPI

## When To Use

Use for FastAPI app setup, route modules, dependencies, request and response schemas, database integration, and queue-backed flows.

## Core Rules

- Inspect the existing app factory, router layout, dependency style, and session lifecycle first.
- Keep route handlers thin.
- Match the repo's sync or async database style.

## Preferred Patterns

- Clear request and response schemas.
- Dependency injection through the framework's existing pattern.
- Commit-before-enqueue behavior when a route triggers background work.
- Focused validation around routes and services.

## Anti-Patterns

- Route handlers that own business logic.
- Duplicate app startup, session, or dependency abstractions.
- Mixing sync and async styles without local precedent.

## Checklist

- Inspect the current FastAPI boundary first.
- Confirm session and dependency conventions.
- Load only the matching FastAPI references.
- Validate the changed routes or services.

## References Index

- `references/app-setup.md`
- `references/patterns.md`
- `references/postgres-connection-setup.md`
- `references/celery-integration.md`
