# Authentication application configuration

## Purpose and when to use it

Register the custom user application before the first migration.

## When not to use it

Never change `AUTH_USER_MODEL` after production migrations exist.

## Responsibilities and invariants

The app label and user model name form a permanent schema contract.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
```

## Alternatives and trade-offs

Django's default user is sufficient when username login is acceptable. A custom
model is easiest to adopt at project creation.

## Required tests

`manage.py check` must resolve `authentication.User` as the configured model.

## Related standards

- [User model](models.md)
