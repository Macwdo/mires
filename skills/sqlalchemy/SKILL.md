---
name: sqlalchemy
description: SQLAlchemy session, model, and query boundary guidance for repositories that already use SQLAlchemy.
---

# SQLAlchemy

## When To Use

Use when the repository already uses SQLAlchemy and the change touches models, sessions, queries, or transaction boundaries.

## Core Rules

- Reuse the existing engine and session lifecycle.
- Match the repo's sync or async SQLAlchemy style.
- Keep persistence details aligned with the surrounding service boundary.

## Preferred Patterns

- Centralized session creation.
- Model and query code near the existing ownership boundary.
- Focused migrations or schema changes matched to local tooling.

## Anti-Patterns

- Creating a second engine or session factory.
- Mixing sync and async session usage in the same path without precedent.
- Pushing business logic into persistence helpers.

## Checklist

- Confirm the current session lifecycle.
- Confirm where models and queries live today.
- Reuse the migration and validation workflow already in the repo.

## References Index

- `references/session-and-model-boundaries.md`
