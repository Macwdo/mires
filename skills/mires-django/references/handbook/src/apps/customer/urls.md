# Customer routes

## Purpose and when to use it

Expose the ViewSet's standard collection and detail actions.

## When not to use it

Do not add action routes for workflows that belong to jobs or separate domain
resources.

## Responsibilities and invariants

Routes are namespaced and have no duplicate API prefix.

## Complete canonical artifact

<!-- artifact: src/apps/customer/urls.py; profiles: base,full -->
```python
from rest_framework.routers import SimpleRouter

from apps.customer.views import CustomerViewSet

app_name = "customers"

router = SimpleRouter()
router.register("", CustomerViewSet, basename="customer")

urlpatterns = router.urls
```

## Alternatives and trade-offs

Explicit `path()` declarations make each action visible but duplicate router
behavior for conventional CRUD.

## Required tests

Reverse list and detail names and verify the `/api/v1/customers/` prefix.

## Related standards

- [Customer ViewSet](views.md)
- [API composition](../api/urls.md)
