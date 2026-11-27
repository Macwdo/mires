# Cross-Origin Requests

## Purpose and when to use it

Use `django-cors-headers` to let a browser-based frontend on a different
origin call this API with credentials.

## When not to use it

Do not widen `CORS_ALLOWED_ORIGINS` to `"*"` alongside
`CORS_ALLOW_CREDENTIALS`; browsers reject that combination and it is unsafe
for a cookie- or credentialed-header-bearing API regardless.

## Responsibilities and invariants

`corsheaders` is appended to [base](base.md)'s `INSTALLED_APPS` and its
middleware is inserted immediately before `CommonMiddleware`, matching the
package's own placement requirement. Allowed origins are explicit and
environment-driven; there is no default origin in a non-local environment.

## Complete canonical artifact

<!-- artifact: src/core/settings/cors.py; profiles: base -->
```python
from decouple import Csv, config

from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.append("corsheaders")
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "corsheaders.middleware.CorsMiddleware",
)

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
```

## Alternatives and trade-offs

`CORS_ALLOWED_ORIGINS` lists exact origins rather than using
`CORS_ALLOWED_ORIGIN_REGEXES`; a regex invites an accidentally permissive
pattern and this project's frontends are a small, known set.

## Required tests

A preflight `OPTIONS` request from an allowed origin succeeds; one from an
unlisted origin is not granted `Access-Control-Allow-Origin`.

## Related standards

See [base](base.md), [security](security.md), and
[environment](../../../environment.md).
