---
name: macwdo-python-django-services-functions
description: "Macwdo Django function-based service guidance. Use for write-side business logic, keyword-only service APIs, type annotations, full_clean before save, and entity_action naming."
---

# Django Services Functions

Use this skill when adding write-side business logic in a Django app.

## Rules

- Services own business rules, state changes, and side effects.
- Prefer function-based services by default.
- Use keyword-only arguments unless the service takes zero or one argument.
- Type annotate service inputs and return values.
- Prefer names such as `invoice_create`, `invoice_send`, or `invoice_cancel`.
- Call `full_clean()` before `save()` when the service owns persistence for new or materially changed models.

## Example

```python
from apps.example.models import ExampleModel


def example_create(*, account, name: str) -> ExampleModel:
    example = ExampleModel(account=account, name=name)
    example.full_clean()
    example.save()
    return example
```
