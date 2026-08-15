# Security Headers and Cookies

## Purpose and when to use it

Use this module for CSRF origins, cookie flags, and the HSTS/TLS-related
security headers that must differ between local and production.

## When not to use it

Do not toggle these values per view; they are process-wide and derived once
from `IS_PRODUCTION`.

## Responsibilities and invariants

Every cookie- and transport-security flag that must be `True` in production
and may be relaxed locally derives from the single `IS_PRODUCTION` value in
[base](base.md), so there is one place that can get this wrong instead of
eight.

## Complete canonical artifact

<!-- artifact: src/core/settings/security.py; profiles: base -->
```python
from decouple import Csv, config

from .base import IS_PRODUCTION

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_HSTS_SECONDS = 31_536_000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
```

## Alternatives and trade-offs

`SECURE_PROXY_SSL_HEADER` trusts `X-Forwarded-Proto` unconditionally; this
is only safe behind a reverse proxy that strips client-supplied forwarding
headers, per [security](../../../docs/security.md).

## Required tests

Test that production settings enable every secure flag and that local
settings do not require TLS.

## Related standards

See [base](base.md), [cors](cors.md), and
[security](../../../docs/security.md).
