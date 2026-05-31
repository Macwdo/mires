---
name: macwdo-python-django-serializers-input
description: "Macwdo DRF input serializer guidance. Use for request bodies, query params, action payloads, serializers.Serializer validation, field validation, and cross-field validation."
---

# Django Serializers Input

Use this skill when an endpoint needs request-body, query-parameter, or action-payload validation.

## Rules

- Use a dedicated input serializer when the endpoint accepts structured data.
- Use `serializers.Serializer` for request payloads, query params, custom action payloads, and non-trivial validation flows.
- Keep validation in serializers and business rules in services.
- Use `validate_<field>` for per-field normalization and `validate()` for cross-field validation.
- Use `raise_exception=True` when validating in views or actions.

## Example

```python
from rest_framework import serializers


class ExampleSerializerRequest(serializers.Serializer):
    name = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        return value.strip()
```
