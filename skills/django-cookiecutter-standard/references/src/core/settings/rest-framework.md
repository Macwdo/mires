# Django REST Framework Configuration

## Purpose and when to use it

Use this module for every DRF-wide default: authentication, permissions,
throttling, filtering, pagination, and error handling.

## When not to use it

Do not set per-view DRF options here; only cross-cutting defaults belong in
this module, and views override them explicitly.

## Responsibilities and invariants

API throttles combine anonymous, authenticated-user, burst, and
endpoint-scoped limits, each independently overridable through its own
environment variable.

## Complete canonical artifact

<!-- artifact: src/core/settings/rest_framework.py; profiles: base -->
```python
from decouple import config

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "apps.api.throttling.BurstRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("API_THROTTLE_ANON", default="100/hour"),
        "user": config("API_THROTTLE_USER", default="2000/day"),
        "burst": config("API_THROTTLE_BURST", default="60/minute"),
        "registration": config("API_THROTTLE_REGISTRATION", default="5/hour"),
        "token": config("API_THROTTLE_TOKEN", default="10/minute"),
        "token_refresh": config("API_THROTTLE_TOKEN_REFRESH", default="30/minute"),
        "token_verify": config("API_THROTTLE_TOKEN_VERIFY", default="60/minute"),
        "customers": config("API_THROTTLE_CUSTOMERS", default="600/hour"),
    },
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.api.pagination.StableCursorPagination",
    "EXCEPTION_HANDLER": "apps.api.exceptions.api_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}
```

## Alternatives and trade-offs

DRF's application throttles are cache-backed fairness controls, not a
denial-of-service boundary. Django's default local-memory cache is
sufficient for deterministic local examples but counts separately in every
process. Production deployments must use a shared cache for consistent
application limits and enforce authoritative abuse controls at the trusted
reverse proxy, API gateway, or edge.

## Required tests

Test throttle rejection per scope and the exception handler's error shape.

## Related standards

See [base](base.md), [jwt](jwt.md), and
[API design](../../../docs/api-design.md).
