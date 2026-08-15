# Stable cursor pagination

## Purpose and when to use it

Use cursor pagination for mutable collections where offset pages would skip or
duplicate records.

## When not to use it

Use explicit bounded pages when clients require random page access or a total
count.

## Responsibilities and invariants

Ordering ends with the unique primary key, page size is bounded, and clients
treat cursors as opaque.

## Complete canonical artifact

<!-- artifact: src/apps/api/pagination.py; profiles: base,full -->
```python
from rest_framework.pagination import CursorPagination


class StableCursorPagination(CursorPagination):
    page_size = 50
    cursor_query_param = "cursor"
    ordering = ("-created_at", "-id")
```

## Alternatives and trade-offs

Cursor pagination is stable and efficient but cannot provide arbitrary page
jumps or a cheap exact total.

## Required tests

Insert tied timestamps and records between requests; assert no duplicates or
omissions while following cursors.

## Related standards

- [Customer collection](../customer/views.md)
