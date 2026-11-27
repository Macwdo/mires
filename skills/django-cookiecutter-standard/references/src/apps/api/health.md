# Health checks

## Purpose and when to use it

Use liveness to detect a running process and readiness to decide whether the
instance can serve traffic.

## When not to use it

Do not call third-party services from liveness or expose exception details.

## Responsibilities and invariants

The database readiness check is bounded by the database connection timeout and
returns only a boolean status.

## Complete canonical artifact

<!-- artifact: src/apps/api/health.py; profiles: base,full -->
```python
from django.db import DatabaseError, connection


def database_is_ready() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except DatabaseError:
        return False
```

## Alternatives and trade-offs

Deep dependency checks offer more detail but can amplify an outage and cause
healthy processes to restart. Keep optional dependencies out of base readiness.

## Required tests

Mock success and database failure without requiring an external database outage.

## Related standards

- [Health views](views.md)
