# Versioned API routes

## Purpose and when to use it

Compose the base API under the project-level `/api/v1/` prefix.

## When not to use it

Do not mount admin, metrics, or static media below the public API namespace.

## Responsibilities and invariants

Every application owns its child URL configuration and namespace.

## Complete canonical artifact

<!-- artifact: src/apps/api/urls.py; profiles: base,full -->
```python
from django.urls import include, path

from apps.api.views import LivenessView, ReadinessView

app_name = "api"

urlpatterns = [
    path("live/", LivenessView.as_view(), name="live"),
    path("ready/", ReadinessView.as_view(), name="ready"),
    path("auth/", include("apps.authentication.urls", namespace="auth")),
    path("customers/", include("apps.customer.urls", namespace="customers")),
]
```

## Alternatives and trade-offs

Header-based versioning keeps URLs stable but is harder to inspect, cache, and
link. Path versioning makes compatibility boundaries explicit.

## Required tests

Reverse all public route names and assert the expected versioned paths.

## Related standards

- [Authentication routes](../authentication/urls.md)
- [Customer routes](../customer/urls.md)
