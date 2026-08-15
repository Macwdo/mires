---
name: postgres-connection-setup
description: Mires's FastAPI and Postgres connection setup pattern for Python repos. Use for SQLAlchemy engine and sessionmaker lifecycle, FastAPI lifespan startup and shutdown, request-scoped Session or AsyncSession dependencies, sync versus async SQLAlchemy choices, Alembic expectations, service session boundaries, and worker session safety.
---

# FastAPI SQLAlchemy Connection Setup

Use this skill when wiring SQLAlchemy into a FastAPI app or reviewing whether database resources are scoped correctly.

## Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing database/session setup, sync versus async choice, settings source, lifespan/app factory pattern, and Alembic wiring override the examples below. Treat source repo signals as examples only when they match the target repository.

## Core Rules

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

Repo-aligned source signals:

- `src/app.py:23` defines FastAPI `lifespan`.
- `src/app.py:27` creates the app-lifetime async engine and stores it on `app.state.engine`.
- `src/db/database.py:11` centralizes engine creation and disposal.
- `src/api/dependencies/database.py:6` yields one session per request.
- `alembic/env.py:20` and `alembic/env.py:69` show Alembic using settings and async migrations instead of production startup `create_all()`.

## Recommended Sync Shape

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

## Async Variant

Use async SQLAlchemy only when the project has an async driver such as `asyncpg` and async route/service boundaries. This repo is in that category: `pyproject.toml` includes `asyncpg`, `src/config.py` expects an async PostgreSQL DSN, `src/app.py` manages the async engine in lifespan, and `src/api/dependencies/database.py` yields request-scoped async sessions.

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

It is also acceptable to create the async engine during `lifespan` and store it on `app.state` when matching an existing app like this repo. Even in that variant, the engine must still be app-lifetime, not request-lifetime.

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

## Project Shape

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

## Final Checklist

- No global `Session`.
- No engine creation per request.
- The database dependency uses `yield`.
- Lifespan shutdown disposes the engine.
- Production code does not rely on `create_all()`.
- Routes receive `Session` or `AsyncSession` through `Depends`.
- Settings are not hardcoded in production-ready code.
- Alembic is used or explicitly recommended for production migrations.
- Background tasks create their own database resources instead of reusing request sessions.
