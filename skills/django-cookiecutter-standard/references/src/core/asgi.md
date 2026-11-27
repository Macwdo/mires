# ASGI Application

## Purpose and when to use it

The base ASGI artifact supports Django's async request stack. Realtime profiles may replace it with Channels routing.

## When not to use it

Prefer WSGI for a synchronous REST-only deployment when operational simplicity matters most.

## Responsibilities and invariants

Initialize Django before importing any application code that may touch models.

## Complete canonical artifact

<!-- artifact: src/core/asgi.py; profiles: base -->
```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
```

<!-- artifact: src/core/asgi.py; profiles: realtime-channels,realtime,full -->
```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django_application = get_asgi_application()

from apps.realtime.auth import JwtAuthMiddleware  # noqa: E402
from apps.realtime.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                JwtAuthMiddleware(
                    URLRouter(websocket_urlpatterns),
                )
            )
        ),
    }
)
```

## Alternatives and trade-offs

Channels adds protocol routing and Redis only when WebSockets are required.

## Required tests

Import the application and smoke-test it with an ASGI test client.

## Related standards

See [SSE](../../recipes/sse.md), [Channels](../../recipes/channels.md), and [operations](../../docs/operations.md).
