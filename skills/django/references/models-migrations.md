---
name: models-migrations
description: "Mires Django model migration guidance. Use after model edits to create and inspect migrations, apply migrations, and update adjacent admin, serializers, selectors, views, services, and tests."
---

# Django Models Migrations

Use this skill after changing Django model fields, constraints, relationships, or model classes.

## Rules

- Create migrations when model state changes.
- Inspect generated migrations before applying them.
- Update `admin.py` and `apps.py` when a new model or app shape requires it.
- Update serializers, selectors, views, services, and tests that expose the model.
- Run the project migration commands when available; this repo family commonly uses `make migrations` and `make migrate`.

## Checklist

- Migration exists for model changes.
- Admin and app config are still correct.
- User-visible model behavior has tests or manual validation.
