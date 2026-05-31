---
name: macwdo-python-django-models-base-classes
description: "Macwdo Django model base-class guidance. Use for choosing AppBaseModel, AccountRelatedModel, and through-model inheritance in repo-style Django apps."
---

# Django Models Base Classes

Use this skill when adding or changing a Django model class.

## Rules

- Inspect the app `models.py`, `admin.py`, `apps.py`, and migrations before introducing new model patterns.
- Use `AppBaseModel` for standalone entities.
- Use `AppBaseModel, AccountRelatedModel` for account-scoped entities.
- Use `AppBaseModel` for junction or through models unless the local app already does something different.
- Import shared base classes from `apps.common.models` and account scope from `apps.account.models` when those modules exist.

## Example

```python
from apps.account.models import AccountRelatedModel
from apps.common.models import AppBaseModel


class ExampleModel(AppBaseModel, AccountRelatedModel):
    ...
```
