---
name: macwdo-python-django-tests-authenticated-api
description: "Macwdo authenticated DRF API test guidance. Use for api_client_with_common_user tests, reverse route names, status and body assertions, and database state assertions after mutations."
---

# Django Tests Authenticated API

Use this skill when testing an authenticated DRF endpoint.

## Rules

- Use the project authenticated API client fixture when available, commonly `api_client_with_common_user`.
- Destructure the tuple into `api_client, user` for clarity.
- Use `reverse()` with the real route name.
- Assert the HTTP status code and full response body.
- For mutations, assert the resulting database state after the call.
- Use `@pytest.mark.django_db` on tests that touch the database.
