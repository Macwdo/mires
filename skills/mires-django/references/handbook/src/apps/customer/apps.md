# Customer application configuration

## Purpose and when to use it

Register the Customer teaching application with Django.

## When not to use it

Do not use startup hooks for customer data synchronization.

## Responsibilities and invariants

The application label remains stable for schema and content-type references.

## Complete canonical artifact

<!-- artifact: src/apps/customer/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class CustomerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customer"
```

## Alternatives and trade-offs

Implicit app configuration is shorter but less explicit.

## Required tests

`manage.py check` validates application loading.

## Related standards

- [Customer application](README.md)
