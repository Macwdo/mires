# Customer model

## Purpose and when to use it

Store a generic contact record owned by one account.

## When not to use it

Do not add authentication, billing, or vendor-specific fields to this teaching
model.

## Responsibilities and invariants

Account ownership is mandatory, string output is safe for logs, and the default
index supports tenant-scoped newest-first listing.

## Complete canonical artifact

<!-- artifact: src/apps/customer/models.py; profiles: base,full -->
```python
from django.db import models

from apps.account.models import AccountOwnedModel


class Customer(AccountOwnedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    objects = models.Manager()

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = (
            models.Index(
                fields=("account", "-created_at", "-id"),
                name="customer_account_created_idx",
            ),
        )

    def __str__(self) -> str:
        return f"Customer({self.pk}, {self.name})"
```

## Alternatives and trade-offs

Normalizing phone numbers and email addresses into separate models helps
multi-value contacts but adds joins and domain policy not needed for base CRUD.

## Required tests

Test required ownership, default ordering, index migration parity, and timestamp
population.

## Related standards

- [Account-owned base](../account/models.md)
- [Migration generation](../../../docs/reconstruction.md#migration-generation)
