---
name: tests-pagination
description: "Mires DRF pagination test guidance. Use for list endpoint response shapes with next, previous, results, order-sensitive payloads, and pagination assertions."
---

# Django Tests Pagination

Use this skill when testing DRF list endpoints.

## Rules

- Assert the full paginated response shape, not just the results array.
- Use the repo pagination convention for `next`, `previous`, and `results`.
- Assert ordering when list order is part of the endpoint contract.
- Create enough data to prove filtering, scope, or pagination behavior when relevant.
- Keep setup in helpers when repeated across list tests.

## Expected Shape

```python
assert response.json() == {
    "next": None,
    "previous": None,
    "results": [...],
}
```
