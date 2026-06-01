---
name: tests-tdd-workflow
description: "Mires Django TDD workflow guidance. Use for red-green-refactor cycles with pytest, DRF, helpers, route names, response assertions, persisted database state, and helper cleanup."
---

# Django Tests TDD Workflow

Use this skill when adding tests for Django models, serializers, views, services, or DRF endpoints.

## Rules

- Inspect the app `tests/`, `helpers.py`, and `conftest.py` before adding setup code.
- Reuse existing helper names, auth fixtures, route naming, and response assertion style.
- Start from user-visible behavior or the API contract.
- Make the smallest production change that satisfies the failing test.
- Move repeated setup into `tests/helpers.py` during refactor.

## Workflow

1. RED: write the failing behavior test first.
2. GREEN: implement the smallest code change.
3. REFACTOR: improve repeated setup and helper clarity.
