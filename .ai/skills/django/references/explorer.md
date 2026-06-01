---
name: explorer
description: "Explore Django reference categories inside the django skill. Use when selecting the specific Django reference files to load."
---

# Django Explorer

Use this guide to select the specific Django reference files that match the task. Load only the references that correspond to the touched subsystem.

## Reference Categories

- Models: `.ai/skills/django/references/models-base-classes.md`, `.ai/skills/django/references/models-fields-relationships.md`, `.ai/skills/django/references/models-migrations.md`
- Services: `.ai/skills/django/references/services-functions.md`, `.ai/skills/django/references/services-transactions.md`, `.ai/skills/django/references/services-exceptions.md`
- Selectors: `.ai/skills/django/references/selectors-detail.md`, `.ai/skills/django/references/selectors-list.md`, `.ai/skills/django/references/selectors-optimization.md`
- Serializers: `.ai/skills/django/references/serializers-input.md`, `.ai/skills/django/references/serializers-output.md`, `.ai/skills/django/references/serializers-boundaries.md`
- Endpoints: `.ai/skills/django/references/endpoints-api-view.md`, `.ai/skills/django/references/endpoints-routing.md`, `.ai/skills/django/references/endpoints-responses.md`
- Tests and bootstrap: `.ai/skills/django/references/tests-tdd-workflow.md`, `.ai/skills/django/references/tests-authenticated-api.md`, `.ai/skills/django/references/project-bootstrap.md`

## Selection Rules

- Load the smallest set of references that covers the touched model, service, selector, serializer, endpoint, or test surface.
- Use multiple categories for end-to-end features that cross model, API, and test boundaries.
- Follow existing app conventions when they are stronger than a generic rule.
