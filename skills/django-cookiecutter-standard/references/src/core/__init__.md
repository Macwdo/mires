# Core Package

## Purpose and when to use it

This retained module documents the Python package boundary. It is deliberately free of import-time side effects.

## When not to use it

Do not initialize Celery, Sentry, Django, or network clients from a package initializer.

## Responsibilities and invariants

Importing `core` is safe in management commands, test collection, WSGI, and ASGI processes.

## Complete canonical artifact

<!-- artifact: src/core/__init__.py; profiles: base -->
```python
"""Process configuration for the Django service."""
```

## Alternatives and trade-offs

Tasks import `core.celery` explicitly instead of using a compatibility alias here.

## Required tests

Import `core` without configured external services.

## Related standards

See [Celery](celery.md) and [operations](../../docs/operations.md).
