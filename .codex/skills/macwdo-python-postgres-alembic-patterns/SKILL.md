---
name: macwdo-python-postgres-alembic-patterns
description: Macwdo's Alembic migration patterns for Python Postgres repos. Use for autogenerate output, async env.py configuration, settings-driven database URLs, pgvector extension migrations, downgrade safety, migration Makefile targets, and model-to-migration consistency.
---

# Alembic Patterns

Use this skill when adding migrations, reviewing migration output, or changing Alembic configuration.

For model design rules, use `macwdo-python-postgres-patterns` first. For local infrastructure needed to run migrations, use `macwdo-python-docker-compose-patterns`.

## Source Repo Signals

- Alembic reads the database URL from `src.config.settings.POSTGRES_URI`: `alembic/env.py:20`, `alembic/env.py:24`.
- Autogenerate metadata comes from `Base.metadata` after importing all models: `alembic/env.py:29`, `alembic/env.py:30`, `alembic/env.py:32`.
- Online migrations use `async_engine_from_config`, `NullPool`, and `connection.run_sync(...)`: `alembic/env.py:69`, `alembic/env.py:74`, `alembic/env.py:77`, `alembic/env.py:80`, `alembic/env.py:81`.
- The first migration enables pgvector before vector columns are created: `alembic/versions/27d27688b18f_enable_pgvector_extension.py:21`, `alembic/versions/27d27688b18f_enable_pgvector_extension.py:23`.
- The schema migration depends on the pgvector extension migration: `alembic/versions/11e4864688e5_alembic.py:17`.
- Vector columns require the `pgvector` import in generated migrations: `alembic/versions/11e4864688e5_alembic.py:13`, `alembic/versions/11e4864688e5_alembic.py:92`.
- Makefile migration commands are the local interface: `Makefile:32`, `Makefile:36`, `Makefile:40`, `Makefile:44`, `Makefile:48`, `Makefile:52`.

## Migration Workflow

1. Update SQLAlchemy models.
2. Start local database infrastructure if needed: `make up` or `docker compose -f docker-compose-dev.yml up -d db`.
3. Create a migration with `make m-create`.
4. Inspect the generated file before applying it.
5. Adjust extension ordering, enum handling, indexes, constraints, and downgrades manually.
6. Apply with `make m-apply`.
7. Verify state with `make m-current` or `make m-history`.

## Async Env Rules

- Keep Alembic's URL sourced from settings so migrations use the same `.env` contract as the app.
- Keep all model imports reachable before `target_metadata = Base.metadata`.
- Use `async_engine_from_config(...)` for asyncpg URLs and run migrations through `connection.run_sync(...)`.
- Use `pool.NullPool` for migration engines.
- Do not create an app engine from `src/db/database.py` inside Alembic env; Alembic owns its migration engine.

## Autogenerate Review Rules

- Autogenerate is a draft. Always inspect the migration.
- Preserve extension migrations before vector columns.
- Check enum changes carefully. Postgres enum alterations often need manual SQL.
- Check downgrade order: drop dependent join tables before parent tables.
- Check indexes and unique constraints on lookup fields.
- Keep generated imports minimal but complete, especially `pgvector`.
- Use descriptive migration messages instead of placeholder names when creating new migrations.

## pgvector Rules

- Create the extension with `CREATE EXTENSION IF NOT EXISTS vector`.
- Do not drop the extension in a downgrade if existing data or other tables may still depend on it, unless the migration is clearly isolated and safe.
- If changing `settings.EMBEDDING_DIMENSION`, plan how existing vector data will be rewritten or discarded.

## Checklist

- `alembic/env.py` still imports all models and points at `Base.metadata`.
- Migration applies against a fresh local Postgres database.
- Migration applies after the current head.
- Downgrade is present and ordered.
- pgvector extension and vector columns are ordered correctly.
- Makefile commands remain the documented migration entrypoint.
