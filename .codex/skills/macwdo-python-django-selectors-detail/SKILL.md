---
name: macwdo-python-django-selectors-detail
description: "Macwdo Django detail selector guidance. Use for reusable single-object reads, scoped querysets, missing-object behavior, select_related, prefetch_related, and typed selector signatures."
---

# Django Selectors Detail

Use this skill when adding reusable read access to one object or a scoped queryset.

## Rules

- Selectors own read paths, filtering, query composition, and queryset optimization.
- Use keyword-only arguments unless the selector takes zero or one argument.
- Type annotate selector inputs and return values.
- Use account, user, or visibility scope in the selector when access rules require it.
- Be consistent about missing-object behavior: return `None`, return a queryset for endpoint `get_object_or_404`, or raise a repo-standard exception.

## Example

```python
def example_get(*, example_id, account) -> ExampleModel | None:
    return (
        ExampleModel.objects.select_related("account")
        .prefetch_related("tags")
        .filter(id=example_id, account=account)
        .first()
    )
```
