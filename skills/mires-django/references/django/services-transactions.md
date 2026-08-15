---
name: services-transactions
description: "Mires Django service transaction guidance. Use for transaction.atomic, multi-row writes, invariants, transaction.on_commit side effects, and keeping transaction boundaries out of serializers."
---

# Django Services Transactions

Use this skill when a Django service writes multiple rows, enforces invariants, or dispatches side effects.

## Rules

- Use `@transaction.atomic` when the service writes multiple rows, enforces invariants, or coordinates related mutations.
- Keep transaction boundaries in the service layer instead of the serializer layer.
- Use `transaction.on_commit()` for side effects that should only run after the database commit succeeds.
- Do not enqueue tasks, send emails, or call external systems before the database state they depend on is durable.
- Test both successful persistence and relevant failure behavior.

## Example

```python
from django.db import transaction


@transaction.atomic
def example_create(*, account, name: str):
    example = ExampleModel(account=account, name=name)
    example.full_clean()
    example.save()
    transaction.on_commit(lambda: example_created_task.delay(example_id=example.id))
    return example
```
