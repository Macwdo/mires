# SQLAlchemy Session And Model Boundaries

- Reuse the existing engine and session factory.
- Match the repository's sync or async session style.
- Keep query and model changes close to the existing ownership boundary.
- Avoid adding a second persistence abstraction unless the repo already uses one.

## Async Helper Shape

When a project already uses async SQLAlchemy, keep engine construction and session creation centralized. Dispose app- or worker-lifetime engines explicitly:

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@asynccontextmanager
async def get_engine(*, postgres_uri: PostgresDsn) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(str(postgres_uri), pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@asynccontextmanager
async def get_session(
    *,
    engine: AsyncEngine,
    expire_on_commit: bool = False,
) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=expire_on_commit)
    async with session_factory() as session:
        yield session
```
