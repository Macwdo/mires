---
name: macwdo-python-django-endpoints-responses
description: "Macwdo DRF response guidance. Use for explicit status codes, public endpoint auth settings, output serialization, object fetching, pagination, filtering, and failure response assertions."
---

# Django Endpoints Responses

Use this skill when finishing endpoint response behavior.

## Rules

- Return explicit status codes for both success and failure paths.
- Serialize output explicitly instead of relying on hidden serializer side effects.
- For public endpoints, set `permission_classes = []` and `authentication_classes = []`.
- For read-only endpoints, prefer `self.get_object()`, `self.get_queryset()`, or selectors that keep object fetching consistent with the rest of the app.
- Keep pagination, filtering, and queryset optimization aligned with existing base views or pagination classes.
- Tests should assert both status code and response body.
