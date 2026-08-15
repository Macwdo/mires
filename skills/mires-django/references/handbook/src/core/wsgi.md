# WSGI Application

## Purpose and when to use it

Use Gunicorn with WSGI for synchronous REST deployments.

## When not to use it

Use ASGI when the service owns SSE or WebSocket connections.

## Responsibilities and invariants

This module performs no configuration beyond choosing `core.settings`.

## Complete canonical artifact

<!-- artifact: src/core/wsgi.py; profiles: base -->
```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
```

## Alternatives and trade-offs

See the deployment comparison before mixing WSGI and ASGI worker pools.

## Required tests

Import `application` and smoke-test one request through Gunicorn.

## Related standards

See [ASGI](asgi.md) and [operations](../../docs/operations.md).
