# Transactional Customer import service

## Purpose and when to use it

Use this service when a job or administrative endpoint must validate and create
several Customer records atomically.

## When not to use it

Single-record API CRUD stays in the ModelViewSet and serializer.

## Responsibilities and invariants

Every row is assigned the caller's account, all rows validate before the first
insert, and the transaction creates all records or none.

## Complete canonical artifact

<!-- artifact: src/apps/customer/services.py; profiles: base,full -->
```python
from collections.abc import Iterable, Mapping
from typing import Any

from django.db import transaction

from apps.account.models import Account
from apps.customer.models import Customer


@transaction.atomic
def import_customers(
    *,
    account: Account,
    rows: Iterable[Mapping[str, Any]],
) -> list[Customer]:
    customers = [
        Customer(
            account=account,
            name=str(row["name"]),
            email=str(row.get("email", "")),
            phone=str(row.get("phone", "")),
            notes=str(row.get("notes", "")),
        )
        for row in rows
    ]
    for customer in customers:
        customer.full_clean()
    return Customer.objects.bulk_create(customers)
```

## Alternatives and trade-offs

Row-by-row creation gives individual signals and simpler attribution of a
database failure. Bulk insertion reduces queries but deliberately bypasses
`save()` and signals, so validation is explicit.

## Required tests

Test one-account assignment, successful bulk creation, and complete rollback
when any row is invalid.

## Related standards

- [Direct CRUD](views.md)
- [Service boundaries](../../README.md)
