# Common Django application configuration

## Purpose and when to use it

Register the common package with Django so model metadata is deterministic.

## When not to use it

Do not perform startup I/O or import domain models from `ready()`.

## Responsibilities and invariants

The application label and default primary-key type must remain stable after the
first migration ships.

## Complete canonical artifact

<!-- artifact: src/apps/common/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
```

## Alternatives and trade-offs

Implicit configuration is shorter but makes application metadata less obvious.

## Required tests

`manage.py check` validates application loading.

## Related standards

- [Common foundations](README.md)
