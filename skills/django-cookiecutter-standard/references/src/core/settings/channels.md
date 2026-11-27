# Channel Layer Settings

## Purpose and when to use it

Use this module for the Redis URL shared by Celery's broker/cache use cases
and, when `channels_redis` is installed, the ASGI channel layer.

## When not to use it

Do not configure `CHANNEL_LAYERS` unconditionally; a reconstruction that
excludes `realtime-channels` never installs `channels_redis`, and this
module must stay importable in that case.

## Responsibilities and invariants

`CHANNEL_LAYERS` is only defined when `module_exists("channels_redis")` is
true, mirroring [sentry](sentry.md)'s optional-dependency gate.

## Complete canonical artifact

<!-- artifact: src/core/settings/channels.py; profiles: base -->
```python
from decouple import config

from .base import module_exists

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")
if module_exists("channels_redis"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
```

## Required tests

Settings import without `channels_redis` installed; a WebSocket round trip
succeeds when it is installed.

## Related standards

See [base](base.md) and [channels](../../../recipes/channels.md).
