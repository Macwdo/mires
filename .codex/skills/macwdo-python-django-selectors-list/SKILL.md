---
name: macwdo-python-django-selectors-list
description: "Macwdo Django list selector guidance. Use for filtered querysets, django-filter FilterSet classes, ordering, account scoping, and keeping filtering out of views."
---

# Django Selectors List

Use this skill when building list endpoints or reusable filtered queryset logic.

## Rules

- Keep filtering and optimization in selectors instead of scattering it across views.
- Use `django_filters.FilterSet` when the repo uses django-filter for request filters.
- Apply account or user scope before returning a queryset.
- Set stable ordering in the selector when endpoint order matters.
- Return the shape that best fits the caller: queryset, list, dict, or computed collection.

## Example

```python
class ExampleFilter(django_filters.FilterSet):
    class Meta:
        model = ExampleModel
        fields = ("status", "is_active")


def example_list(*, account, filters: dict | None = None):
    filters = filters or {}
    queryset = ExampleModel.objects.filter(account=account).order_by("-created_at")
    return ExampleFilter(filters, queryset).qs
```
