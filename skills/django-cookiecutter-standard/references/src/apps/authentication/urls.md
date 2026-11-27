# Authentication URL surface

## Purpose and when to use it

Mount a stable, namespaced JWT and identity API under `/api/v1/auth/`.

## When not to use it

Do not expose token endpoints under multiple aliases; duplicated routes
complicate client migration and rate limiting.

## Responsibilities and invariants

Token obtain, refresh, verify, logout, registration, and current-user routes
have explicit names. Public token operations use distinct throttle scopes so
credential checks and refresh traffic can be tuned independently.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/urls.py; profiles: base,full -->
```python
from django.urls import path

from apps.authentication.views import (
    LogoutView,
    MeView,
    RegistrationView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
)

app_name = "auth"

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "token/",
        ThrottledTokenObtainPairView.as_view(),
        name="token",
    ),
    path(
        "token/refresh/",
        ThrottledTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "token/verify/",
        ThrottledTokenVerifyView.as_view(),
        name="token-verify",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
```

## Alternatives and trade-offs

An external identity provider can add federation and managed risk controls but
introduces network dependency and provider lifecycle concerns. IP-based
application throttling reduces accidental and low-volume abuse; credential
stuffing still requires edge controls, monitoring, and risk-aware
authentication policy.

## Required tests

Reverse every named route, exercise the complete token lifecycle, and verify
that each public credential route returns 429 at its configured threshold.

## Related standards

- [Authentication views](views.md)
