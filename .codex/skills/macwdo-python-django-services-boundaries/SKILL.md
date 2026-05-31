---
name: macwdo-python-django-services-boundaries
description: "Macwdo Django service boundary guidance. Use for keeping writes in services, reads in selectors, endpoints thin, serializers validation-only, and avoiding business logic in managers, save methods, or signals."
---

# Django Services Boundaries

Use this skill when deciding where Django business logic belongs.

## Rules

- Keep endpoints thin: validate input, call a selector or service, return a response.
- Keep serializers focused on validation and representation, not business writes.
- Keep services focused on pushing state changes, business rules, and side effects.
- Do not hide write-side business logic in views, serializers, managers, querysets, model `save()`, or signals.
- If a service becomes read-heavy and stops mutating state, move the fetch logic into a selector.
- Start with `services.py`; split into a `services/` package only when the app grows multiple service domains.
