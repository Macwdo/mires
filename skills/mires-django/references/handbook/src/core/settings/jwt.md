# JWT Configuration

## Purpose and when to use it

Use this module for `djangorestframework-simplejwt`'s token lifetimes and
rotation behavior.

## When not to use it

Do not lengthen `ACCESS_TOKEN_LIFETIME` to avoid refresh calls; short-lived
access tokens limit the blast radius of a leaked token.

## Responsibilities and invariants

Refresh tokens rotate and are blacklisted after rotation, so a stolen
refresh token stops working the next time the legitimate client refreshes.

## Complete canonical artifact

<!-- artifact: src/core/settings/jwt.py; profiles: base -->
```python
from datetime import timedelta

from .base import SECRET_KEY

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

## Alternatives and trade-offs

Signing with `SECRET_KEY` avoids a second secret to rotate; a dedicated JWT
signing key would let JWT rotation happen independently of the Django
session/CSRF secret at the cost of one more required production variable.

## Required tests

Test access token expiry, refresh rotation, and blacklist rejection of a
reused refresh token.

## Related standards

See [base](base.md), [rest_framework](rest-framework.md), and
[authentication](../../apps/authentication/README.md).
