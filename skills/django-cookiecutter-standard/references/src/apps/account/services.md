# Account creation service

## Purpose and when to use it

Call this service inside registration or an administrative provisioning
transaction.

## When not to use it

Do not call it on every login or hide it in a model signal.

## Responsibilities and invariants

The operation is idempotent for one user and never changes an existing
account's active state.

## Complete canonical artifact

<!-- artifact: src/apps/account/services.py; profiles: base,full -->
```python
from apps.account.models import Account
from apps.authentication.models import User


def ensure_account(*, user: User) -> tuple[Account, bool]:
    return Account.objects.get_or_create(user=user)
```

## Alternatives and trade-offs

`get_or_create` makes provisioning retry-safe. A plain create is stricter but
turns harmless delivery retries into integrity failures.

## Required tests

Calling the service twice returns the same account and reports creation once.

## Related standards

- [Registration transaction](../authentication/services.md)
