# Root URL Configuration

## Purpose and when to use it

This is the stable process-level URL boundary.

## When not to use it

Application endpoints belong in their app URL modules.

## Responsibilities and invariants

Admin is isolated under `/admin/`; versioned JSON APIs are under `/api/v1/`.

## Complete canonical artifact

<!-- artifact: src/core/urls.py; profiles: base -->
```python
from importlib.util import find_spec

from django.contrib import admin
from django.urls import include, path


def module_exists(name: str) -> bool:
    try:
        return find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
]

OPTIONAL_URLS = (
    ("api/v1/jobs/", "apps.jobs.urls"),
    ("api/v1/files/", "apps.files.urls"),
    ("api/v1/events/", "apps.realtime.urls"),
)
for prefix, module in OPTIONAL_URLS:
    if module_exists(module):
        urlpatterns.append(path(prefix, include(module)))
```

## Alternatives and trade-offs

Host-based routing is appropriate only when separate domains have distinct security boundaries.

## Required tests

Reverse every named health, auth, and Customer route.

## Related standards

See [API URLs](../apps/api/urls.md).
