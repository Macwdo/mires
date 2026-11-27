# Celery Settings

## Purpose and when to use it

Use this module for the Celery app configuration consumed by
[`core.celery`](../celery.md): broker, result backend, and task
reliability flags.

## When not to use it

Do not put task definitions or the `Celery()` app instance here; those
belong in `core.celery` and each app's `tasks.py`.

## Responsibilities and invariants

Tasks acknowledge late and are rejected (requeued) on worker loss, so a
killed worker does not silently drop in-flight work.

## Complete canonical artifact

<!-- artifact: src/core/settings/celery.py; profiles: base -->
```python
from decouple import config

from .base import TIME_ZONE

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="django-db")
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = TIME_ZONE
```

## Required tests

Settings import without `django_celery_results`/`django_celery_beat`
installed; a task submitted against the configured broker is picked up by a
worker.

## Related standards

See [base](base.md), [core.celery](../celery.md), and
[celery recipes](../../../recipes/celery/README.md).
