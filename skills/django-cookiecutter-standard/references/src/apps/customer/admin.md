# Customer administration

## Purpose and when to use it

Allow authorized staff to inspect generic Customer records.

## When not to use it

Do not rely on admin list filters as a substitute for application-level tenant
authorization.

## Responsibilities and invariants

Ownership and timestamps are read-only; searches avoid notes to limit expensive
unbounded text scans.

## Complete canonical artifact

<!-- artifact: src/apps/customer/admin.py; profiles: base,full -->
```python
from django.contrib import admin

from apps.customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "account", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "phone", "account__user__email")
    readonly_fields = ("account", "created_at", "updated_at")
    ordering = ("-created_at", "-id")
```

## Alternatives and trade-offs

Removing account records from admin entirely reduces support capability but
also reduces the impact of staff mistakes.

## Required tests

Admin smoke tests verify list and change views for authorized staff.

## Related standards

- [Customer model](models.md)
