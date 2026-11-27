# Gunicorn Configuration

## Purpose and when to use it

Use Gunicorn for synchronous REST under WSGI.

## Complete canonical artifact

<!-- artifact: gunicorn.conf.py; profiles: base -->
```python
import multiprocessing

from decouple import config

bind = config("GUNICORN_BIND", default="0.0.0.0:8000")
workers = config("GUNICORN_WORKERS", default=min(multiprocessing.cpu_count() * 2 + 1, 8), cast=int)
worker_class = "sync"
timeout = config("GUNICORN_TIMEOUT", default=30, cast=int)
graceful_timeout = config("GUNICORN_GRACEFUL_TIMEOUT", default=30, cast=int)
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
capture_output = True
```

## Responsibilities and invariants

Bound worker counts prevent accidental overcommit. Long-lived realtime connections are not served by sync workers.

## Required tests

Smoke-test startup, graceful termination, liveness, and one authenticated endpoint.
