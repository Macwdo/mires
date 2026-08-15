---
name: explorer
description: "Explore Django reference categories inside the django skill. Use when selecting the specific Django reference files to load."
---

# Django Explorer

Use this guide to select the specific Django reference files that match the task. Load only the references that correspond to the touched subsystem.

## Reference Categories

- Models: `skills/mires-django/references/django/models-base-classes.md`, `skills/mires-django/references/django/models-fields-relationships.md`, `skills/mires-django/references/django/models-migrations.md`
- Services: `skills/mires-django/references/django/services-functions.md`, `skills/mires-django/references/django/services-transactions.md`, `skills/mires-django/references/django/services-exceptions.md`
- Selectors: `skills/mires-django/references/django/selectors-detail.md`, `skills/mires-django/references/django/selectors-list.md`, `skills/mires-django/references/django/selectors-optimization.md`
- Serializers: `skills/mires-django/references/django/serializers-input.md`, `skills/mires-django/references/django/serializers-output.md`, `skills/mires-django/references/django/serializers-boundaries.md`
- Endpoints: `skills/mires-django/references/django/endpoints-api-view.md`, `skills/mires-django/references/django/endpoints-routing.md`, `skills/mires-django/references/django/endpoints-responses.md`
- Tests and bootstrap: `skills/mires-django/references/django/tests-tdd-workflow.md`, `skills/mires-django/references/django/tests-authenticated-api.md`, `skills/mires-django/references/django/project-bootstrap.md`

## Selection Rules

- Load the smallest set of references that covers the touched model, service, selector, serializer, endpoint, or test surface.
- Use multiple categories for end-to-end features that cross model, API, and test boundaries.
- Follow existing app conventions when they are stronger than a generic rule.
