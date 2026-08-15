---
name: endpoints-routing
description: "Mires DRF routing guidance. Use for DefaultRouter registration, route prefixes without trailing slashes, basename when queryset is omitted, namespaced reverse calls, and router-backed ViewSet actions."
---

# Django Endpoints Routing

Use this skill when wiring DRF ViewSets and routes.

## Rules

- Register router prefixes without a trailing slash.
- If the ViewSet omits a class-level `queryset`, provide `basename=` when registering it with the router.
- Register ViewSets with a router instead of wiring `@action` methods manually.
- Keep action-specific settings such as `serializer_class`, `permission_classes`, `url_path`, and `detail` on the `@action` itself.
- Use `reverse()` with route names in tests instead of hardcoded URLs.

## Example

```python
from rest_framework.routers import DefaultRouter

from apps.example.views import ExampleViewSet

router = DefaultRouter()
router.register("examples", ExampleViewSet, basename="example")

urlpatterns = router.urls
```
