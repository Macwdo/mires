---
name: macwdo-python-django-tests-drf-rules
description: "Macwdo DRF test rules. Use for pytest.mark.django_db, reverse URLs, response body assertions, mutation database assertions, and module-level external-service mocks."
---

# Django Tests DRF Rules

Use this skill as the checklist for DRF endpoint tests.

## Rules

- Use `@pytest.mark.django_db` on every test that touches the database.
- Use `reverse()`, never hardcoded URLs.
- Assert both HTTP status and response body.
- For mutations, assert the resulting database state.
- Mock external services at the module where they are used.
- For list endpoints, assert the paginated response shape used by the repo.
