---
name: serializers-action-aware
description: "Mires DRF action-aware serializer guidance. Use for ViewSet get_serializer_class maps, per-action serializers, and differing input/output serializers for one action."
---

# Django Serializers Action Aware

Use this skill when a ViewSet needs different serializers for list, retrieve, create, or custom actions.

## Rules

- Implement `get_serializer_class()` explicitly when a ViewSet needs per-action serializers.
- Keep a `serializer_action_classes` map on the ViewSet when that matches local style.
- If one action has different input and output serializers, validate with the input serializer and instantiate the output serializer for the response.
- Keep action serializer choices close to the ViewSet so routes remain easy to inspect.
- Do not make a single serializer carry unrelated request and response responsibilities.
