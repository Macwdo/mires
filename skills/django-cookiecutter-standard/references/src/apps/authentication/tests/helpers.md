# Authentication test helpers

## Purpose and when to use it

Keep token acquisition explicit without duplicating endpoint payloads.

## When not to use it

Tests for login failure should make their own request and assert the response.

## Responsibilities and invariants

The helper asserts successful login before returning both token strings.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/helpers.py; profiles: base,full -->
```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

DEFAULT_PASSWORD = "Correct-Horse-Battery-Staple-42"


def obtain_tokens(
    *,
    client: APIClient,
    email: str,
    password: str = DEFAULT_PASSWORD,
) -> tuple[str, str]:
    response = client.post(
        reverse("api:auth:token"),
        {"email": email, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    return payload["access"], payload["refresh"]
```

## Alternatives and trade-offs

Constructing tokens directly is faster but bypasses the actual login contract.

## Required tests

JWT lifecycle tests exercise this helper through the real endpoint.

## Related standards

- [JWT lifecycle tests](test_tokens.md)
