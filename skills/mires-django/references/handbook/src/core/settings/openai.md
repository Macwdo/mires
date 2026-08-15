# OpenAI Settings

## Purpose and when to use it

Use this module for the OpenAI credentials and model names consumed by the
[vector/AI recipes](../../../recipes/vector.md).

## When not to use it

Do not read `OPENAI_API_KEY` directly in application code; import from this
module so tests can override it in one place.

## Responsibilities and invariants

`OPENAI_SAFETY_IDENTIFIER_SECRET` falls back to `SECRET_KEY` so a
reconstruction that never sets it still has a stable, non-guessable per-
deployment value to derive a safety identifier from.

## Complete canonical artifact

<!-- artifact: src/core/settings/openai.py; profiles: base -->
```python
from decouple import config

from .base import SECRET_KEY

OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-5.6-sol")
OPENAI_EMBEDDING_MODEL = config(
    "OPENAI_EMBEDDING_MODEL",
    default="text-embedding-3-small",
)
OPENAI_EMBEDDING_DIMENSIONS = config("OPENAI_EMBEDDING_DIMENSIONS", default=1536, cast=int)
OPENAI_SAFETY_IDENTIFIER_SECRET = config(
    "OPENAI_SAFETY_IDENTIFIER_SECRET",
    default=SECRET_KEY,
)
```

## Required tests

Settings import with `OPENAI_API_KEY` unset; embedding calls use
`OPENAI_EMBEDDING_DIMENSIONS` to validate vector width.

## Related standards

See [base](base.md) and [vector](../../../recipes/vector.md).
