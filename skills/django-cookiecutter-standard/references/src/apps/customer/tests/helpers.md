# Customer test helpers

## Purpose and when to use it

Create a Customer through the public API when endpoint setup is not itself the
assertion.

## When not to use it

Isolation tests should create cross-account records directly so ownership is
unambiguous.

## Responsibilities and invariants

The helper fails immediately unless API creation succeeds.

## Complete canonical artifact

<!-- artifact: src/apps/customer/tests/helpers.py; profiles: base,full -->
```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.customer.models import Customer


def create_customer(
    *,
    client: APIClient,
    name: str = "Example Customer",
    email: str = "customer@example.com",
) -> Customer:
    response = client.post(
        reverse("api:customers:customer-list"),
        {"name": name, "email": email},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return Customer.objects.get(pk=response.json()["id"])
```

## Alternatives and trade-offs

Direct ORM setup is faster and better when the API contract is unrelated to
the test.

## Required tests

CRUD tests use this helper only after creation behavior has its own assertion.

## Related standards

- [Customer endpoint tests](test_views.md)
