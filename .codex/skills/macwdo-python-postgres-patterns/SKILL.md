---
name: macwdo-python-postgres-patterns
description: Macwdo's Postgres and pgvector data modeling patterns for Python repos. Use for SQLAlchemy 2.x models, asyncpg Postgres URLs, pgvector embeddings, processing status tables, indexes, relationships, transactions, and database-backed application state.
---

# Postgres Patterns

Use this skill when changing database models, queries, transactions, or Postgres-backed application state.

For FastAPI engine/session wiring, use `macwdo-python-fastapi-postgres-connection-setup`. For schema migrations, use `macwdo-python-postgres-alembic-patterns`.

## Source Repo Signals

- Settings require an async Postgres DSN: `src/config.py:8`.
- Runtime database access uses SQLAlchemy async engines and sessions: `src/db/database.py:11`, `src/db/database.py:20`, `src/db/database.py:36`.
- Models use SQLAlchemy 2.x typed mappings with a shared `Base`: `src/db/models/base.py:15`, `src/db/models/base.py:18`.
- Common timestamps are inherited from `Base`: `src/db/models/base.py:19`, `src/db/models/base.py:20`.
- Processing state is represented with `ProcessingStatus`: `src/db/models/base.py:8`.
- Product embeddings use `pgvector.sqlalchemy.VECTOR` and a settings-driven dimension: `src/db/models/product.py:5`, `src/db/models/product.py:38`.
- Product SKU and normalized brand/category names are indexed and unique: `src/db/models/product.py:21`, `src/db/models/product.py:56`, `src/db/models/product.py:65`.
- Grouping uses both direct `Product.group_id` and an explicit `group_products` join model: `src/db/models/product.py:27`, `src/db/models/group.py:34`.
- Local Postgres uses the pgvector image: `docker-compose-dev.yml:4`.

## Model Rules

- Use SQLAlchemy 2.x `Mapped[...]` and `mapped_column(...)`.
- Put shared id and timestamp fields on `Base`.
- Add `__tablename__` explicitly for every model.
- Use `ForeignKey(...)` plus `relationship(..., back_populates=...)` on both sides.
- Use `TYPE_CHECKING` imports for relationship-only type hints to avoid import cycles.
- Keep enum status columns backed by the shared `ProcessingStatus` when they represent background work.
- Add indexes or unique constraints on natural lookup keys such as SKU and normalized names.
- Do not call `Base.metadata.create_all()` for app startup. Use Alembic.

## pgvector Rules

- Keep vector dimension tied to `settings.EMBEDDING_DIMENSION`.
- Ensure an Alembic migration creates the `vector` extension before tables with vector columns.
- Store embeddings on the model that owns similarity behavior; in this repo that is `Product.embedding`.
- When changing embedding dimensions, treat it as a data migration concern, not only a model edit.

## Transaction Rules

- Use one request-scoped `AsyncSession` for API handlers.
- Use `async with db.get_session(engine=engine) as session, session.begin():` for service workflows that own their transaction.
- Use `flush()` and `refresh()` when generated ids are needed before returning or relating objects.
- Commit processing rows before enqueueing background tasks.
- Worker services should open their own session from a worker-local engine.

## Query Rules

- Prefer `select(Model)` and `await session.execute(...)` or `await session.scalars(...)`.
- Use `selectinload(...)` for relationships returned through API responses.
- Avoid lazy-load surprises in response serialization. Load relationships before building nested Pydantic responses.

## Review Checklist

- Model changes have matching Alembic migrations.
- New foreign keys have relationships and back-populates where useful.
- Background workflows persist `pending`, `processing`, `completed`, and `failed` states consistently.
- Vector extension and vector columns are ordered correctly in migrations.
- Tests or manual verification cover transaction boundaries for status updates.
