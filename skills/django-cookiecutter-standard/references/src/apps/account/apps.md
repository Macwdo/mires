# Account application configuration

## Purpose and when to use it

Register the account models without startup side effects.

## When not to use it

Do not create accounts from signals in `ready()`; registration owns that
transaction explicitly.

## Responsibilities and invariants

The application label is a migration contract.

## Complete canonical artifact

<!-- artifact: src/apps/account/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.account"
```

## Alternatives and trade-offs

Signals appear convenient but obscure transaction boundaries and complicate
bulk imports.

## Required tests

`manage.py check` and migration checks validate registration.

## Related standards

- [Registration service](../authentication/services.md)
