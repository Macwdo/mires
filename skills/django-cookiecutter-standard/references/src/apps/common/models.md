# Timestamped models

## Purpose and when to use it

Inherit `TimeStampedModel` for persistent domain records that need creation and
last-modification timestamps.

## When not to use it

Do not inherit it for join tables or immutable event records whose timestamps
have different semantics.

## Responsibilities and invariants

- Timestamps are server assigned and read-only at the API boundary.
- The base is abstract and creates no table.
- Concrete models choose indexes based on their query patterns.

## Complete canonical artifact

<!-- artifact: src/apps/common/models.py; profiles: base,full -->
```python
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

## Alternatives and trade-offs

Database-generated timestamps improve cross-writer consistency but require
database-specific expressions. Django-managed values are portable and adequate
when the application is the only writer.

## Required tests

Domain model tests verify timestamps are populated and updates advance
`updated_at`.

## Related standards

- [Account-owned models](../account/models.md)
