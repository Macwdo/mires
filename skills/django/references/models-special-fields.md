---
name: models-special-fields
description: "Mires Django model specialized-field guidance. Use for derived @property values, pgvector VectorField embeddings, and deciding when values should or should not be stored."
---

# Django Models Special Fields

Use this skill when a Django model needs derived values, embeddings, or non-standard fields.

## Rules

- Use `@property` for derived values that do not need storage.
- Only use `VectorField` when the app already uses pgvector or the task explicitly requires embeddings.
- Keep embedding dimensions and vector behavior aligned with the existing app configuration.
- Do not store a computed value unless queries, constraints, or performance make persistence necessary.
- Add tests around public behavior that depends on specialized fields.

## Examples

```python
@property
def is_valid(self) -> bool:
    return bool(self.upload_finished_at)
```

```python
from pgvector.django import VectorField

embedding = VectorField(dimensions=1536)
```
