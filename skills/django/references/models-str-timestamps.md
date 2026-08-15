---
name: models-str-timestamps
description: "Mires Django model string and timestamp guidance. Use for fmt_model_str, FK traversal in __str__, default ordering, and inherited created_at/updated_at fields."
---

# Django Models Str Timestamps

Use this skill when implementing model display, ordering, or timestamp behavior.

## Rules

- Always use `fmt_model_str` for `__str__` when the repo provides it.
- Include stable fields such as `id`, `name`, or a useful foreign-key traversal in the display fields.
- Foreign-key traversal such as `user__email` is allowed when it improves readability.
- Set `Meta.ordering = ["-created_at"]` when the model needs the repo-standard newest-first ordering.
- Do not redeclare timestamp fields inherited from `AppBaseModel`.

## Example

```python
from apps.common.models import fmt_model_str


def __str__(self) -> str:
    return fmt_model_str(self, fields=["id", "name"])


class Meta:
    ordering = ["-created_at"]
```
