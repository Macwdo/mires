---
name: macwdo-python-fastapi-app-setup
description: Macwdo's FastAPI application setup pattern for Python repos. Use for app factory or entrypoint layout, lifespan-managed app state, router registration, dependency modules, Pydantic request and response schemas, thin route handlers, service boundaries, and preferred HTTPException error handling.
---

# FastAPI App Setup

Use this skill when adding or reviewing standalone FastAPI app setup, routes, dependencies, schemas, settings, or HTTP error handling.

## Source Repo Signals

- App setup uses async lifespan to create one SQLAlchemy async engine and store it on `app.state.engine`: `src/app.py:23`, `src/app.py:27`.
- Routers are imported at the app boundary and included with explicit prefixes and tags: `src/app.py:7`, `src/app.py:36`.
- Request handlers receive sessions through `Depends(get_db_session)`, which pulls the engine from `request.app.state`: `src/api/dependencies/database.py:6`.
- API dependencies are small factory functions in `src/api/dependencies`: database at `src/api/dependencies/database.py:6`, AWS clients at `src/api/dependencies/aws.py:6`.
- Route schemas usually live beside routes, with Pydantic `BaseModel` request and response models: `src/api/routes/files/schemas.py:6`, `src/api/routes/groups/schemas.py:8`, `src/api/routes/products/schemas.py:6`.
- ORM response schemas use `model_config = {"from_attributes": True}` where models are returned through Pydantic validation: `src/api/routes/files/schemas.py:15`, `src/api/routes/groups/schemas.py:31`.

## Preferred Shape

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

## Rules

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

## Anti-Patterns To Correct

- Avoid `raise Response(...)` for errors. Several source routes do this, but new FastAPI code should raise `HTTPException`: `src/api/routes/products/routes.py:22`, `src/api/routes/groups/routes.py:48`, `src/api/routes/vendor/routes.py:54`.
- Avoid returning raw `Response` for ordinary JSON API errors unless custom response body behavior is intended: `src/api/routes/files/routes.py:54`.
- Avoid mixing `async with session.begin()` and manual `commit()` inside the same block unless the transaction behavior is intentional and tested: `src/api/routes/files/routes.py:36`, `src/api/routes/files/routes.py:41`.
- Avoid defining schemas inline in a route module once a domain has multiple endpoints; the vendor route does this at `src/api/routes/vendor/routes.py:12`.
