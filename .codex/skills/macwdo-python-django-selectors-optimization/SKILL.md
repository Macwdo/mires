---
name: macwdo-python-django-selectors-optimization
description: "Macwdo Django selector optimization guidance. Use for select_related, prefetch_related, annotations, avoiding N+1 serialization, and locating heavy read-path logic in selectors."
---

# Django Selectors Optimization

Use this skill when a read path risks N+1 queries, heavy annotations, or repeated filtering logic.

## Rules

- Use `select_related()` for foreign keys and one-to-one relationships that would otherwise cause N+1 queries.
- Use `prefetch_related()` for many-to-many and reverse relationships.
- Keep heavy read-path annotations, filtering, and ordering logic in selectors.
- If a computed model property spans multiple relations or would cause N+1 queries during serialization, prefer a selector instead.
- Align optimizations with the response serializer fields and nested representations.
