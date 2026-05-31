---
name: macwdo-python-django-serializers-output
description: "Macwdo DRF output serializer guidance. Use for ModelSerializer read representations, read_only_fields, explicit response fields, computed outputs, and response-only serializers."
---

# Django Serializers Output

Use this skill when shaping data returned from a DRF endpoint.

## Rules

- Use a dedicated output serializer when an endpoint returns structured data.
- Use `ModelSerializer` for straightforward read representations or when the app already exposes the model directly.
- Set explicit `fields` and mark response fields read-only when appropriate.
- Use plain `Serializer` for computed outputs or responses that do not map cleanly to one model.
- Serialize output explicitly in the endpoint instead of relying on hidden side effects.

## Example

```python
class ExampleSerializerResponse(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = ["id", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = fields
```
