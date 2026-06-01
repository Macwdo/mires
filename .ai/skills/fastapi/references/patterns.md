---
name: patterns
description: Mires's FastAPI feature patterns for Python repos. Use for route modules, dependency injection, Pydantic schemas, async SQLAlchemy sessions, router registration, health endpoints, upload/start/status endpoints, service delegation, and HTTP error handling in ml-products-grouping.
---

# FastAPI Patterns

Use this skill when adding or reviewing FastAPI endpoints and API-facing feature work in this repo.

For narrower setup-only work, prefer `app-setup`. For endpoints that enqueue Celery jobs, also use `celery-integration`.

## Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing route layout, dependency injection style, settings pattern, service boundary, sync versus async database style, and error handling override the examples below. Treat source repo signals as examples only when they match the target repository.

## Source Repo Signals

- The FastAPI app is a module-level `app` with an async lifespan-managed database engine: `src/app.py:23`, `src/app.py:27`, `src/app.py:34`.
- Routers are registered in `src/app.py` with explicit prefixes and tags: `src/app.py:36`, `src/app.py:37`, `src/app.py:38`, `src/app.py:39`, `src/app.py:40`.
- Database sessions are yielded through `Depends(get_db_session)` from `request.app.state.engine`: `src/api/dependencies/database.py:6`.
- External clients are exposed through small dependency factories: `src/api/dependencies/aws.py:6`, `src/api/dependencies/aws.py:10`.
- Route modules live under `src/api/routes/<domain>/routes.py`, with schemas beside them when the domain has enough surface: `src/api/routes/files/routes.py:25`, `src/api/routes/products/routes.py:13`, `src/api/routes/groups/routes.py:22`.
- Pydantic response models are explicit on route decorators: `src/api/routes/files/routes.py:25`, `src/api/routes/groups/routes.py:53`, `src/api/routes/products/routes.py:44`.
- Background-work start routes create a processing row, commit it, enqueue a task, and return the processing id: `src/api/routes/products/routes.py:24`, `src/api/routes/products/routes.py:30`, `src/api/routes/products/routes.py:32`, `src/api/routes/groups/routes.py:29`, `src/api/routes/groups/routes.py:35`, `src/api/routes/groups/routes.py:37`.

## Route Layout

Keep each domain route package small and predictable:

```text
src/api/routes/<domain>/
├── __init__.py
├── routes.py
└── schemas.py
```

Use `routes.py` for HTTP orchestration and `schemas.py` for request/response models. Keep business logic in `src/services` or `src/vendor/services`, not in route functions.

## Endpoint Rules

- Use `APIRouter()` in each route module and register it in `src/app.py`.
- Inject database sessions with `Depends(get_db_session)`.
- Inject S3/SQS or other clients through dependency functions under `src/api/dependencies`.
- Keep handlers thin: validate input, load required rows, call a service or enqueue a task, return a schema.
- Commit durable rows before sending Celery tasks.
- Use scalar ids in task calls and responses, not ORM objects.
- Prefer `HTTPException` for new or touched error paths. The current repo sometimes returns or raises `Response`; do not copy that pattern into new work.
- Return Pydantic models or `model_validate(...)` results rather than raw ORM rows.

## Schema Rules

- Use Pydantic `BaseModel` request and response classes.
- Set `model_config = {"from_attributes": True}` for schemas that validate ORM models.
- Keep API schema names explicit: `StartUploadRequest`, `StartUploadResponse`, `ProductProcessingResponse`.
- Expose processing ids and status enums in start/status workflows.

## Async Database Rules

- Use `AsyncSession` from the dependency and SQLAlchemy 2.x `select(...)`.
- Use `await session.flush()` and `await session.refresh(model)` when an id is needed before commit.
- Keep transaction boundaries obvious. If a handler uses `session.begin()`, avoid nested manual commits unless the surrounding block is intentionally structured and tested.
- Do not create engines or long-lived clients inside route functions unless there is no dependency boundary yet.

## Checklist

- New route module is included in `src/app.py` with prefix and tag.
- Request and response schemas live beside the route.
- Database and external resources are injected.
- Business logic is delegated to a service.
- Errors use `HTTPException` on new code.
- Background routes commit processing rows before `.delay()`.
- Status endpoints read application state from the database.
