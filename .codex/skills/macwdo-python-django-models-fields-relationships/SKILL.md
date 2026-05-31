---
name: macwdo-python-django-models-fields-relationships
description: "Macwdo Django model field and relationship guidance. Use for CharField, TextField, BooleanField, optional foreign keys, string model references, related_name, and avoiding circular imports."
---

# Django Models Fields Relationships

Use this skill when adding fields or relations to a Django model.

## Rules

- Reuse existing field names, related names, and model organization when possible.
- Use string references for cross-app relations to avoid circular imports.
- Use `blank=True, default=""` for optional text fields when that matches the app style.
- Use `null=True, blank=True` for optional foreign keys that can be absent.
- Set explicit `related_name` values that are easy to grep.
- Do not redeclare `created_at` or `updated_at`; shared base models provide them.

## Example

```python
from django.db import models


name = models.CharField(max_length=255)
description = models.TextField(blank=True, default="")
is_active = models.BooleanField(default=True)
related = models.ForeignKey(
    "other_app.OtherModel",
    on_delete=models.CASCADE,
    related_name="examples",
)
optional_ref = models.ForeignKey(
    "other_app.OtherModel",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="optional_examples",
)
```
