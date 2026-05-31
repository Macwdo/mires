---
name: macwdo-python-django-models-appconfig-admin
description: "Macwdo Django AppConfig and admin registration guidance. Use when adding apps, registering models with admin decorators, list displays, filters, search fields, readonly fields, and ordering."
---

# Django Models AppConfig Admin

Use this skill when a Django model change needs app configuration or admin registration.

## Rules

- Ensure each app `apps.py` declares `default_auto_field = "django.db.models.BigAutoField"`.
- Set the app config `name` to the full `apps.<app_name>` path used by the project.
- Register every model in `admin.py` with the decorator pattern.
- Use useful `list_display`, `list_filter`, `search_fields`, `readonly_fields`, and `ordering` values.
- Keep admin imports local to the app model module.

## Example

```python
from django.contrib import admin

from apps.example.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ["-created_at"]
```
