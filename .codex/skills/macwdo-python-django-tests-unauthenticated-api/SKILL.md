---
name: macwdo-python-django-tests-unauthenticated-api
description: "Macwdo unauthenticated DRF API test guidance. Use for api_client tests, public versus protected endpoint expectations, 401/403 assertions, and reverse route names."
---

# Django Tests Unauthenticated API

Use this skill when testing access behavior without credentials.

## Rules

- Use the unauthenticated `api_client` fixture.
- Use `reverse()` with the real route name.
- Assert `HTTP_401_UNAUTHORIZED` for endpoints requiring authentication unless the repo expects `403` for that path.
- For public endpoints, assert the public success or validation response explicitly.
- Do not rely on hardcoded URL strings.

## Example

```python
@pytest.mark.django_db
def test_resource_returns_401_when_not_authenticated(api_client: APIClient) -> None:
    """GET resource returns 401 when no auth token is provided."""
    url = reverse("api:example:example-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```
