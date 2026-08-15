# Current-user endpoint tests

## Purpose and when to use it

Verify authenticated user data is allow-listed and anonymous requests fail.

## When not to use it

Do not infer JWT refresh behavior from this endpoint.

## Responsibilities and invariants

Password, permission, and account internals are absent from the response.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_me.py; profiles: base,full -->
```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import User


@pytest.mark.django_db
def test_me_returns_allow_listed_user(
    authenticated_client: APIClient,
    user: User,
) -> None:
    # Arrange
    url = reverse("api:auth:me")

    # Act
    response = authenticated_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user.pk,
        "email": user.email,
        "first_name": "",
        "last_name": "",
    }


@pytest.mark.django_db
def test_me_requires_authentication(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:auth:me")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["request_id"]
```

## Alternatives and trade-offs

Embedding account data can save a request but couples identity and tenancy
contracts. The base keeps the response narrow.

## Required tests

Run both authenticated and anonymous cases for authentication changes.

## Related standards

- [Authentication views](../views.md)
