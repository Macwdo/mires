# Customer ViewSet

## Purpose and when to use it

Provide conventional Customer CRUD with DRF's direct model primitives.

## When not to use it

Do not override create, update, or destroy unless a transaction, effect, or
public contract requires behavior beyond serializer and model operations.

## Responsibilities and invariants

The inherited queryset applies account scoping before every action.
`perform_create` assigns the trusted request account and never reads tenancy
from request data. The named scope adds a resource-specific limit on top of the
global sustained and burst limits.

## Complete canonical artifact

<!-- artifact: src/apps/customer/views.py; profiles: base,full -->
```python
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.api.pagination import StableCursorPagination
from apps.api.views import AccountScopedViewSet
from apps.customer.models import Customer
from apps.customer.serializers import CustomerSerializer


class CustomerViewSet(AccountScopedViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    throttle_scope = "customers"
    pagination_class = StableCursorPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "email", "phone", "notes")
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-created_at", "-id")

    def perform_create(self, serializer: CustomerSerializer) -> None:
        serializer.save(account=self.get_account())
```

## Alternatives and trade-offs

A hand-written APIView offers full control but repeats list, detail, validation,
and status-code behavior that ViewSets already make consistent.

## Required tests

Exercise all actions and prove objects from another account return 404 for
retrieve, patch, and delete.

## Related standards

- [Account scope base](../api/views.md)
- [Customer serializer](serializers.md)
