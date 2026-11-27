# Registration tests

## Purpose and when to use it

Verify the public registration transaction and validation contract.

## When not to use it

Manager unit tests remain responsible for low-level user creation rules.

## Responsibilities and invariants

A successful response excludes the password and creates exactly one account;
invalid input creates neither model.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_register.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User


@pytest.mark.django_db
def test_registration_creates_user_and_account(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:auth:register")
    payload = {
        "email": "New.User@EXAMPLE.com",
        "password": "Correct-Horse-Battery-Staple-42",
        "first_name": "New",
        "last_name": "User",
    }

    # Act
    response = api_client.post(
        url,
        payload,
    )
    user = User.objects.get(email="New.User@example.com")

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.json()) == {"id", "email", "first_name", "last_name"}
    assert user.check_password("Correct-Horse-Battery-Staple-42")
    assert Account.objects.filter(user=user, is_active=True).count() == 1


@pytest.mark.django_db
def test_duplicate_email_uses_error_envelope(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user_factory(email="duplicate@example.com")
    url = reverse("api:auth:register")
    registration = {
        "email": "duplicate@example.com",
        "password": "Correct-Horse-Battery-Staple-42",
    }

    # Act
    response = api_client.post(
        url,
        registration,
    )
    payload = response.json()["error"]

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert payload["code"] == "validation_error"
    assert payload["details"]["email"] == ["A user with this email already exists."]
    assert payload["request_id"]
    assert User.objects.filter(email="duplicate@example.com").count() == 1
```

## Alternatives and trade-offs

Service-only tests diagnose transaction behavior precisely; endpoint tests also
lock serializer and envelope behavior.

## Required tests

Add weak-password and forced account-failure cases when changing registration.

## Related standards

- [Registration serializer](../serializers.md)
- [Registration service](../services.md)
