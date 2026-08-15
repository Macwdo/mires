# Logging Configuration

## Purpose and when to use it

Use this module for the process-wide `LOGGING` dict shared by the web,
worker, and management-command processes.

## When not to use it

Do not configure a logger inside application code; add it to this dict so
every process shares one format and one request-ID filter.

## Responsibilities and invariants

Every log line carries `request_id` through
[`RequestIDLogFilter`](../../apps/api/middleware.md), even for log calls
issued outside of a request-bound view.

## Complete canonical artifact

<!-- artifact: src/core/settings/logging.py; profiles: base -->
```python
from decouple import config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": ("{asctime} {levelname} {name} request_id={request_id} {message}"),
            "style": "{",
        }
    },
    "filters": {
        "request_id": {
            "()": "apps.api.middleware.RequestIDLogFilter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_id"],
        }
    },
    "root": {"handlers": ["console"], "level": config("LOG_LEVEL", default="INFO")},
}
```

## Required tests

Confirm a log line emitted during a request includes that request's
`request_id`.

## Related standards

See [base](base.md) and [middleware](../../apps/api/middleware.md).
