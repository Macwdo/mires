---
name: mires-fastapi
description: "Apply Macwdo's FastAPI standards for app setup, lifespan, routes, dependencies, schemas, SQLAlchemy session wiring, HTTP errors, and Celery-backed endpoints. Use when FastAPI owns the HTTP boundary; pair with $mires-python for services, settings, SQLAlchemy, Postgres, and Celery."
---

# Mires FastAPI

Use this skill with `$mires-python` when FastAPI owns the HTTP boundary. Inspect the repository first; its established conventions override the examples in this skill.

## Snippet-Driven Implementation

Always use the closest FastAPI snippet in this `SKILL.md` as the starting reference for generated code: app setup, route module, dependency, schema, SQLAlchemy session wiring, or Celery-backed endpoint. Compare it with sibling modules in the target repository and adapt names, imports, sync/async style, and settings to local conventions. Services, settings, SQLAlchemy models, Postgres, and Celery tasks follow `$mires-python`.

FastAPI patterns for app setup, routes, dependencies, schemas, database access, and worker integration.

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
- Read the complete FastAPI topic, then apply only the sections relevant to the change.
- Validate the changed routes or services.

---

## FastAPI App Setup

Use this section when adding or reviewing standalone FastAPI app setup, routes, dependencies, schemas, settings, or HTTP error handling.

### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing app factory or entrypoint shape, settings pattern, dependency modules, schema placement, service boundaries, and error handling override the examples below.

### Preferred Shape

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with get_engine(postgres_uri=settings.POSTGRES_URI) as engine:
        app.state.engine = engine
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=health_router, prefix="/health", tags=["Health"])
app.include_router(router=items_router, prefix="/items", tags=["Items"])
```

```python
from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(*, request: Request) -> AsyncGenerator[AsyncSession, None]:
    engine = request.app.state.engine
    async with get_session(engine=engine) as session:
        yield session
```

Keep external clients behind dependency factories too. The helper that builds kwargs can read settings; the dependency constructs the client at the edge so routes and services can receive fakes in tests.

```python
import boto3

from src.services.storage import get_s3_client_kwargs, get_queue_client_kwargs


def get_s3_client():
    return boto3.client("s3", **get_s3_client_kwargs())


def get_queue_client():
    return boto3.client("sqs", **get_queue_client_kwargs())
```

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    item = await session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.model_validate(item)
```

### Rules

- Keep app construction in the app entrypoint unless the repo already uses an app factory.
- Use lifespan for long-lived resources and expose request-scoped handles through dependencies.
- Store long-lived resources on `app.state` only when they belong to the FastAPI process lifetime.
- Keep dependency functions small and place them under a dedicated dependency module.
- Group routes by domain under `src/api/routes/<domain>/routes.py`; place domain schemas beside routes unless they are shared.
- Include routers with explicit prefixes and tags in app setup rather than burying prefixes inside route modules.
- Keep route handlers thin: validate inputs, call services or persistence operations, and shape responses.
- Use Pydantic response models for public API contracts.
- Use `model_validate` with `model_config = {"from_attributes": True}` for ORM-backed responses.
- Raise `HTTPException` for API errors in new code.

### Anti-Patterns To Correct

- Avoid `raise Response(...)` for errors; raise `HTTPException` for ordinary FastAPI error paths.
- Avoid returning raw `Response` for ordinary JSON API errors unless custom response body behavior is intended.
- Avoid mixing `async with session.begin()` and manual `commit()` inside the same block unless the transaction behavior is intentional and tested.
- Avoid defining schemas inline in a route module once a domain has multiple endpoints.

---

## FastAPI Patterns

Use this section when adding or reviewing FastAPI endpoints and API-facing feature work.

For narrower setup-only work, apply FastAPI App Setup above. For endpoints that enqueue Celery jobs, continue to FastAPI Celery Integration later in this document.

### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing route layout, dependency injection style, settings pattern, service boundary, sync versus async database style, and error handling override the examples below.

### Route Layout

Keep each domain route package small and predictable:

```text
src/api/routes/<domain>/
├── __init__.py
├── routes.py
└── schemas.py
```

Use `routes.py` for HTTP orchestration and `schemas.py` for request/response models. Keep business logic in the repository's established service modules, not in route functions.

### Endpoint Rules

- Use `APIRouter()` in each route module and register it in `src/app.py`.
- Inject database sessions with `Depends(get_db_session)`.
- Inject S3/SQS or other clients through dependency functions under `src/api/dependencies`.
- Keep handlers thin: validate input, load required rows, call a service or enqueue a task, return a schema.
- Commit durable rows before sending Celery tasks.
- Use scalar ids in task calls and responses, not ORM objects.
- Prefer `HTTPException` for new or touched error paths.
- Return Pydantic models or `model_validate(...)` results rather than raw ORM rows.

### Schema Rules

- Use Pydantic `BaseModel` request and response classes.
- Set `model_config = {"from_attributes": True}` for schemas that validate ORM models.
- Keep API schema names explicit: `CreateItemRequest`, `CreateItemResponse`, `ItemProcessingResponse`.
- Expose processing ids and status enums in start/status workflows.

### Async Database Rules

- Use `AsyncSession` from the dependency and SQLAlchemy 2.x `select(...)`.
- Use `await session.flush()` and `await session.refresh(model)` when an id is needed before commit.
- Keep transaction boundaries obvious. If a handler uses `session.begin()`, avoid nested manual commits unless the surrounding block is intentionally structured and tested.
- Do not create engines or long-lived clients inside route functions unless there is no dependency boundary yet.

### Checklist

- New route module is included in `src/app.py` with prefix and tag.
- Request and response schemas live beside the route.
- Database and external resources are injected.
- Business logic is delegated to a service.
- Errors use `HTTPException` on new code.
- Background routes commit processing rows before `.delay()`.
- Status endpoints read application state from the database.

---

## FastAPI SQLAlchemy Connection Setup

Use this section when wiring SQLAlchemy into a FastAPI app or reviewing whether database resources are scoped correctly.

### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing database/session setup, sync versus async choice, settings source, lifespan/app factory pattern, and Alembic wiring override the examples below.

### Core Rules

- Keep `Engine` and `sessionmaker` app-wide and long-lived.
- Keep `Session` or `AsyncSession` request-scoped through a `yield` dependency.
- Use FastAPI `lifespan` for startup and shutdown; dispose the engine during shutdown.
- Do not create a new engine per request.
- Do not share a global session across requests.
- Keep transaction boundaries explicit. Routes or services should call `commit()` for writes unless the project intentionally uses a tested unit-of-work dependency.
- Use Alembic for production schema migrations; avoid production startup `create_all()`.
- Prefer SQLAlchemy 2.x imports, typing, and query style.
- Prefer sync SQLAlchemy for new apps unless the project already uses async routes, async drivers, and async SQLAlchemy.
- In background tasks and Celery workers, create a new worker-local session or engine; never reuse a request-scoped session after the request ends.

### Recommended Sync Shape

Use this as the default for new FastAPI projects unless the existing codebase is already async.

```python
from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/mydb"


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok"}
```

### Async Variant

Use async SQLAlchemy only when the project has an async driver such as `asyncpg` and established async route, service, and session boundaries.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/mydb"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
```

It is also acceptable to create the async engine during `lifespan` and store it on `app.state` when matching the target repository. Even in that variant, the engine must still be app-lifetime, not request-lifetime.

```python
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_engine(
    *,
    postgres_uri: PostgresDsn,
    pool_pre_ping: bool = True,
    pool_size: int = 10,
    pool_timeout: int = 30,
    pool_recycle: int = 1800,
) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        url=str(postgres_uri),
        pool_pre_ping=pool_pre_ping,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
    )
    try:
        yield engine
    finally:
        await engine.dispose()
        logger.info("Disposed database engine")


async def get_db_session(*, request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        request.app.state.engine,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with get_engine(postgres_uri=settings.POSTGRES_URI) as engine:
        app.state.engine = engine
        yield
```

### Project Shape

Prefer this structure unless the repo already has a stronger convention:

```text
app/
  main.py
  core/config.py
  db/base.py
  db/session.py
  models/
  repositories/
  services/
  api/routes/
```

Keep `Base` in `db/base.py`, engine and session helpers in `db/session.py`, app construction and lifespan in the app entrypoint, ORM models in `models/`, persistence queries in repositories, business behavior in services, and FastAPI handlers in route modules.

### Final Checklist

- No global `Session`.
- No engine creation per request.
- The database dependency uses `yield`.
- Lifespan shutdown disposes the engine.
- Production code does not rely on `create_all()`.
- Routes receive `Session` or `AsyncSession` through `Depends`.
- Settings are not hardcoded in production-ready code.
- Alembic is used or explicitly recommended for production migrations.
- Background tasks create their own database resources instead of reusing request sessions.

---

## FastAPI Celery Integration

Use this section when an HTTP endpoint starts background work through Celery and the API needs to return a job or processing id.

### Preferred Shape

Use this route shape when a FastAPI endpoint starts background work:

```python
@router.post("/process", response_model=ProcessStartResponse)
async def start_process(
    request: ProcessStartRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    processing = Processing(status=ProcessingStatus.PENDING)
    session.add(processing)
    await session.flush()
    await session.refresh(processing)
    await session.commit()

    process_thing_task.delay(processing_id=processing.id, thing_id=request.thing_id)
    return ProcessStartResponse(processing_id=processing.id, status=processing.status)
```

Use this worker shape for async service delegation:

```python
@shared_task
def process_thing_task(processing_id: int, thing_id: int) -> None:
    async def run() -> None:
        async with db.get_engine(postgres_uri=settings.POSTGRES_URI) as engine:
            await services.process_thing(
                processing_id=processing_id,
                thing_id=thing_id,
                engine=engine,
            )

    asyncio.run(run())
```

### Rules

- Keep route code responsible for validation, initial row creation, enqueueing, and response shaping.
- Commit before enqueue. A worker must never receive an id that is still inside an uncommitted HTTP transaction.
- Keep task payloads stable and serializable: ids, strings, numbers, booleans, and small dicts only.
- Use task status tables when the API needs polling. Model status with a shared enum such as `ProcessingStatus`.
- Let routes expose status reads separately from start endpoints.
- Keep worker services independent of FastAPI request state.
- Make workers receive ids and create their own resources.
- Keep the API contract simple: start endpoint returns processing id and initial status; status endpoint returns current status; result endpoint reads completed data if applicable.

### Anti-Patterns

- Do not enqueue before the processing row is committed.
- Do not pass ORM instances, sessions, clients, files, request objects, or large payloads to tasks.
- Do not make task code depend on FastAPI dependency injection.
- Do not bury `.delay(...)` calls in deep service code when the user-facing operation is an HTTP start endpoint; keep enqueue points visible at the route boundary.
