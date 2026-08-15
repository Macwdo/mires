---
name: django
description: Django and DRF patterns for models, services, selectors, serializers, endpoints, routing, and tests.
---

# Django

## When To Use

Use for Django, DRF, models, services, selectors, serializers, endpoints, routing, migrations, and Django testing.

## Core Rules

- Inspect existing Django app, model, serializer, endpoint, and test conventions first.
- Keep reads and writes in the same boundaries the repo already uses.
- Use focused references instead of loading the entire Django corpus.

## Preferred Patterns

- Thin DRF views or viewsets.
- Explicit service boundaries for writes.
- Selectors or equivalent read-side patterns when the repo uses them.
- Route and serializer patterns that match nearby code.

## Anti-Patterns

- New Django abstractions that duplicate the local pattern.
- Business logic hidden in serializers or models when the repo uses services.
- Broad edits that change multiple Django conventions at once.

## Checklist

- Identify the affected Django boundary.
- Inspect matching local examples.
- Load only the needed reference files.
- Validate with focused Django or DRF tests.

## References Index

- `references/explorer.md`
- `references/project-bootstrap.md`
- `references/models-appconfig-admin.md`
- `references/models-base-classes.md`
- `references/models-fields-relationships.md`
- `references/models-migrations.md`
- `references/models-special-fields.md`
- `references/models-str-timestamps.md`
- `references/services-boundaries.md`
- `references/services-dependencies.md`
- `references/services-exceptions.md`
- `references/services-flow-services.md`
- `references/services-functions.md`
- `references/services-transactions.md`
- `references/selectors-boundaries.md`
- `references/selectors-cached.md`
- `references/selectors-detail.md`
- `references/selectors-list.md`
- `references/selectors-optimization.md`
- `references/serializers-action-aware.md`
- `references/serializers-advanced-functions.md`
- `references/serializers-boundaries.md`
- `references/serializers-input.md`
- `references/serializers-output.md`
- `references/endpoints-api-view.md`
- `references/endpoints-crud-viewsets.md`
- `references/endpoints-responses.md`
- `references/endpoints-routing.md`
- `references/endpoints-service-first-crud.md`
- `references/endpoints-viewset-actions.md`
- `references/tests-authenticated-api.md`
- `references/tests-drf-rules.md`
- `references/tests-forbidden-patterns.md`
- `references/tests-helpers-fixtures.md`
- `references/tests-mocking-external-services.md`
- `references/tests-naming-structure.md`
- `references/tests-pagination.md`
- `references/tests-tdd-workflow.md`
- `references/tests-unauthenticated-api.md`
