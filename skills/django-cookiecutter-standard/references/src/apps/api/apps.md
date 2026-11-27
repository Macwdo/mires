# API application configuration

## Purpose and when to use it

Register API infrastructure with a stable Django application label.

## When not to use it

Do not start network clients or run health checks at import time.

## Responsibilities and invariants

Application startup remains deterministic and side-effect free.

## Complete canonical artifact

<!-- artifact: src/apps/api/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
```

## Alternatives and trade-offs

Implicit configuration is shorter but hides the application contract.

## Required tests

`manage.py check` verifies application loading.

## Related standards

- [API boundary](README.md)
