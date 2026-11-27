# Base pytest fixtures

## Purpose and when to use it

Provide explicit API clients and account-bearing users shared by application
tests.

## When not to use it

Do not hide the state relevant to a test behind large implicit fixture graphs.

## Responsibilities and invariants

Every ordinary user fixture has exactly one active account and passwords are set
through the manager.

## Complete canonical artifact

<!-- artifact: src/conftest.py; profiles: base,full -->
```python
from typing import Any

import pytest
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_factory(db: None) -> Any:
    def create_user(
        *,
        email: str = "user@example.com",
        password: str = "Correct-Horse-Battery-Staple-42",
        account_active: bool = True,
    ) -> User:
        user = User.objects.create_user(email=email, password=password)
        Account.objects.create(user=user, is_active=account_active)
        return user

    return create_user


@pytest.fixture
def user(user_factory: Any) -> User:
    return user_factory()


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client
```

## Alternatives and trade-offs

Model Bakery or Factory Boy scales richer fixture graphs but adds a dependency
and another abstraction to this small base.

## Required tests

The suite itself validates fixture setup on every database-backed test.

## Related standards

- [Authentication test helpers](authentication/tests/helpers.md)
