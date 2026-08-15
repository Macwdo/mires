---
name: explorer
description: "Explore Django reference categories inside the django skill. Use when selecting the specific Django reference files to load."
---

# Django Explorer

Use this guide to select the specific Django reference files that match the task. Load only the references that correspond to the touched subsystem.

## Reference Categories

- Models: `skills/django/references/models-base-classes.md`, `skills/django/references/models-fields-relationships.md`, `skills/django/references/models-migrations.md`
- Services: `skills/django/references/services-functions.md`, `skills/django/references/services-transactions.md`, `skills/django/references/services-exceptions.md`
- Selectors: `skills/django/references/selectors-detail.md`, `skills/django/references/selectors-list.md`, `skills/django/references/selectors-optimization.md`
- Serializers: `skills/django/references/serializers-input.md`, `skills/django/references/serializers-output.md`, `skills/django/references/serializers-boundaries.md`
- Endpoints: `skills/django/references/endpoints-api-view.md`, `skills/django/references/endpoints-routing.md`, `skills/django/references/endpoints-responses.md`
- Tests and bootstrap: `skills/django/references/tests-tdd-workflow.md`, `skills/django/references/tests-authenticated-api.md`, `skills/django/references/project-bootstrap.md`

## Selection Rules

- Load the smallest set of references that covers the touched model, service, selector, serializer, endpoint, or test surface.
- Use multiple categories for end-to-end features that cross model, API, and test boundaries.
- Follow existing app conventions when they are stronger than a generic rule.
