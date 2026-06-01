---
name: postgres
description: Postgres and migration guidance for repositories that already use Postgres-related patterns.
---

# Postgres

## When To Use

Use when the repository already uses Postgres and the change touches schema design, migrations, or Postgres-specific features.

## Core Rules

- Follow the existing migration tool and lifecycle.
- Keep schema changes aligned with the repo's ORM and service boundaries.
- Use Postgres-specific features only when the repo already embraces them or the need is clear.

## Preferred Patterns

- Incremental schema changes.
- Migration files reviewed alongside model changes.
- Postgres-aware indexing and data-shape decisions.

## Anti-Patterns

- Introducing a new migration path.
- Using advanced Postgres features without checking local precedent.
- Coupling migration strategy to one-off feature code.

## Checklist

- Confirm the migration tool and workflow.
- Confirm the touched schema owners.
- Validate migrations and affected queries.

## References Index

- `references/patterns.md`
- `references/alembic-patterns.md`
