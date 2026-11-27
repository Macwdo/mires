# Atomic registration service

## Purpose and when to use it

Use this service for the multi-model registration workflow.

## When not to use it

Simple user field updates belong in serializers or model forms; they do not
need a service layer.

## Responsibilities and invariants

User and account creation commit together, and duplicate email races surface as
a normal validation error at the API boundary.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/services.py; profiles: base,full -->
```python
from django.db import transaction

from apps.account.services import ensure_account
from apps.authentication.models import User


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    ensure_account(user=user)
    return user
```

## Alternatives and trade-offs

A post-save signal reduces call-site code but hides failures and can create
partial side effects outside the intended transaction.

## Required tests

Force account creation to fail and assert the user is rolled back; retry
account provisioning independently to prove idempotency.

## Related standards

- [Account service](../account/services.md)
- [Registration endpoint](views.md)
