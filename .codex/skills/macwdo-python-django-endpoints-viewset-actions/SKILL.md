---
name: macwdo-python-django-endpoints-viewset-actions
description: "Macwdo DRF ViewSet action guidance. Use for @action methods, resource-adjacent behavior, action serializer_class, detail/url_path settings, service calls, and explicit output serializers."
---

# Django Endpoints ViewSet Actions

Use this skill when behavior belongs on an existing resource.

## Rules

- Use `@action` when the behavior is adjacent to an existing ViewSet resource.
- Set action-specific `detail`, `methods`, `serializer_class`, and `url_path` on the decorator.
- Use `self.get_serializer(data=request.data)` for action input when the decorator provides the serializer.
- Use `self.get_object()` for detail actions when the action mutates or reads the current resource.
- Call a service for writes and serialize output explicitly.
