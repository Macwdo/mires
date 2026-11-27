# Account-isolated Customer CRUD

## Purpose and when to use it

Use this application as the base example of straightforward Django models,
`ModelSerializer`, and DRF `ModelViewSet` CRUD.

## When not to use it

Do not introduce a service or selector merely to forward one ORM call. Use
services for transactions or effects and selectors for genuinely reusable,
complex reads.

## Responsibilities and invariants

- Every Customer belongs to one account.
- Querysets are account-scoped before retrieve, update, and delete.
- The request cannot choose or change the account foreign key.
- Search and ordering use allow-lists; pagination has stable ordering.

## Complete canonical artifact

<!-- artifact: src/apps/customer/__init__.py; profiles: base,full -->
```python
"""Account-isolated customer records."""
```

## Alternatives and trade-offs

Separate request and response serializers can provide stricter asymmetry, but a
small CRUD resource remains clearer with one carefully configured
`ModelSerializer`.

## Required tests

Cover CRUD, authentication, filtering, stable pagination, inactive accounts,
and cross-account denial for reads, updates, and deletes.

## Related standards

- [Customer model](models.md)
- [Customer API](views.md)
- [Account scoping](../api/views.md)
