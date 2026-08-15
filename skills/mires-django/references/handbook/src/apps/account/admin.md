# Account administration

## Purpose and when to use it

Provide staff with a searchable account status view.

## When not to use it

The admin is not a customer-facing tenancy API.

## Responsibilities and invariants

Account ownership is read-only after creation to avoid accidental tenant
transfer.

## Complete canonical artifact

<!-- artifact: src/apps/account/admin.py; profiles: base,full -->
```python
from django.contrib import admin

from apps.account.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__email",)
    readonly_fields = ("user", "created_at", "updated_at")
```

## Alternatives and trade-offs

A dedicated operations UI can enforce richer workflows but adds a separate
surface to secure and maintain.

## Required tests

Admin smoke tests verify the changelist for an authorized staff user.

## Related standards

- [Account models](models.md)
