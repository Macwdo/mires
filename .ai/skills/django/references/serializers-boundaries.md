---
name: serializers-boundaries
description: "Mires DRF serializer boundary guidance. Use for keeping serializers focused on validation and representation, avoiding business writes in create/update/validate, and using context only when necessary."
---

# Django Serializers Boundaries

Use this skill when deciding what logic belongs in a DRF serializer.

## Rules

- Serializer code should validate input and shape output; it should not become the home of business writes.
- Do not move business writes into `create()` or `update()` unless the repo already treats that serializer as a thin adapter over a service.
- Do not hide orchestration, task dispatch, or side effects in `validate()`.
- Pass `context` only when the serializer genuinely needs request-aware behavior for representation or validation.
- Keep nested serializers and computed fields readable; if output optimization grows complex, refetch and serialize deliberately.
