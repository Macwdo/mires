# Django

Django and DRF patterns for models, services, selectors, serializers, endpoints, routing, and tests.

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

- `references/django/explorer.md`
- `references/django/project-bootstrap.md`
- `references/django/models-appconfig-admin.md`
- `references/django/models-base-classes.md`
- `references/django/models-fields-relationships.md`
- `references/django/models-migrations.md`
- `references/django/models-special-fields.md`
- `references/django/models-str-timestamps.md`
- `references/django/services-boundaries.md`
- `references/django/services-dependencies.md`
- `references/django/services-exceptions.md`
- `references/django/services-flow-services.md`
- `references/django/services-functions.md`
- `references/django/services-transactions.md`
- `references/django/selectors-boundaries.md`
- `references/django/selectors-cached.md`
- `references/django/selectors-detail.md`
- `references/django/selectors-list.md`
- `references/django/selectors-optimization.md`
- `references/django/serializers-action-aware.md`
- `references/django/serializers-advanced-functions.md`
- `references/django/serializers-boundaries.md`
- `references/django/serializers-input.md`
- `references/django/serializers-output.md`
- `references/django/endpoints-api-view.md`
- `references/django/endpoints-crud-viewsets.md`
- `references/django/endpoints-responses.md`
- `references/django/endpoints-routing.md`
- `references/django/endpoints-service-first-crud.md`
- `references/django/endpoints-viewset-actions.md`
- `references/django/tests-authenticated-api.md`
- `references/django/tests-drf-rules.md`
- `references/django/tests-forbidden-patterns.md`
- `references/django/tests-helpers-fixtures.md`
- `references/django/tests-mocking-external-services.md`
- `references/django/tests-naming-structure.md`
- `references/django/tests-pagination.md`
- `references/django/tests-tdd-workflow.md`
- `references/django/tests-unauthenticated-api.md`
