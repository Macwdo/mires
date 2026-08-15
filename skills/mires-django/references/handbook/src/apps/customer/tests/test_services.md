# Customer service tests

## Purpose and when to use it

Verify the bulk import service's atomic validation and ownership rules.

## When not to use it

Endpoint CRUD is covered separately.

## Responsibilities and invariants

One invalid row prevents all inserts.

## Complete canonical artifact

<!-- artifact: src/apps/customer/tests/test_services.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.core.exceptions import ValidationError

from apps.customer.models import Customer
from apps.customer.services import import_customers


@pytest.mark.django_db
def test_import_customers_assigns_one_account(
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="import@example.com")
    rows = [
        {"name": "First", "email": "first@example.com"},
        {"name": "Second", "phone": "+1-555-0101"},
    ]

    # Act
    created = import_customers(
        account=user.account,
        rows=rows,
    )

    # Assert
    assert len(created) == 2
    assert Customer.objects.filter(account=user.account).count() == 2


@pytest.mark.django_db
def test_import_customers_validates_before_inserting(
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="rollback@example.com")
    rows = [
        {"name": "Valid"},
        {"name": "Invalid", "email": "not-an-email"},
    ]

    # Assert
    with pytest.raises(ValidationError):
        import_customers(
            account=user.account,
            rows=rows,
        )
    assert not Customer.objects.filter(account=user.account).exists()
```

## Alternatives and trade-offs

Per-row error collection is friendlier for large imports but changes the
all-or-nothing contract and requires explicit result reporting.

## Required tests

Run successful ownership and pre-insert validation cases.

## Related standards

- [Import service](../services.md)
