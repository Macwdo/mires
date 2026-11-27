# Account and account-owned models

## Purpose and when to use it

Use `Account` as request tenancy context and inherit `AccountOwnedModel` for
every record whose visibility belongs to one account.

## When not to use it

Global reference data and user-owned security records should not inherit the
tenant base.

## Responsibilities and invariants

- Deleting a user deletes its single account and account-owned data.
- The abstract foreign key uses a predictable `account` field.
- Models do not infer an account from process-local or global state.

## Complete canonical artifact

<!-- artifact: src/apps/account/models.py; profiles: base,full -->
```python
from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Account(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account",
    )
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Account({self.pk})"


class AccountOwnedModel(TimeStampedModel):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )

    class Meta:
        abstract = True
```

## Alternatives and trade-offs

A membership table supports collaboration but requires an explicit active
account strategy. The base keeps the safer one-to-one invariant.

## Required tests

Test the one-to-one constraint, cascade behavior, and inactive-account denial.

## Related standards

- [Account creation](services.md)
- [Request scoping](../api/views.md)
