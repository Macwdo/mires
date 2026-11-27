# Customer serializer

## Purpose and when to use it

Validate the small Customer CRUD contract directly from the model.

## When not to use it

Use separate command and response serializers when write and read contracts
meaningfully diverge.

## Responsibilities and invariants

Account ownership and timestamps are read-only; writable fields have explicit
allow-listing.

## Complete canonical artifact

<!-- artifact: src/apps/customer/serializers.py; profiles: base,full -->
```python
from rest_framework import serializers

from apps.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer[Customer]):
    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
```

## Alternatives and trade-offs

Plain serializers make every field rule visible but duplicate valid model
metadata and need hand-written create and update methods.

## Required tests

Test required name, email validation, length limits, partial updates, and
absence of the account field in input and output.

## Related standards

- [Customer model](models.md)
- [Customer ViewSet](views.md)
