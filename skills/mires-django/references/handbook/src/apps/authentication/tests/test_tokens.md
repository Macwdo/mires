# JWT lifecycle tests

## Purpose and when to use it

Prove access authentication, refresh rotation, old-token blacklisting, and
explicit logout revocation.

## When not to use it

Do not mock Simple JWT in lifecycle tests; mocks would bypass the security
properties under test.

## Responsibilities and invariants

Old refresh tokens stop working immediately after rotation or logout while
newly issued access tokens authenticate.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_tokens.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.helpers import DEFAULT_PASSWORD, obtain_tokens


@pytest.mark.django_db
def test_refresh_rotates_and_blacklists_old_token(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="jwt@example.com", password=DEFAULT_PASSWORD)
    access, refresh = obtain_tokens(client=api_client, email=user.email)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Act
    authenticated = api_client.get(reverse("api:auth:me"))
    api_client.credentials()
    rotated = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )
    reused = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )

    # Assert
    assert authenticated.status_code == status.HTTP_200_OK
    assert rotated.status_code == status.HTTP_200_OK
    assert rotated.json()["refresh"] != refresh
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="logout@example.com", password=DEFAULT_PASSWORD)
    access, refresh = obtain_tokens(client=api_client, email=user.email)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Act
    response = api_client.post(
        reverse("api:auth:logout"),
        {"refresh": refresh},
    )
    api_client.credentials()
    reused = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED
```

## Alternatives and trade-offs

Shorter access-token lifetime narrows the remaining logout window but increases
refresh traffic.

## Required tests

Keep rotation, reuse denial, logout, and invalid-token cases in the base suite.

## Related standards

- [JWT routes](../urls.md)
- [Authentication policy](../README.md)
