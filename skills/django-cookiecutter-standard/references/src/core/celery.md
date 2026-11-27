# Celery Application

## Purpose and when to use it

Use this artifact whenever `celery-core` (or any module requiring it, such as `celery-django` or `chat-streaming`) is part of the resolved reconstruction.

## When not to use it

Do not enqueue work that must commit atomically before the surrounding database transaction. Use `transaction.on_commit`.

## Responsibilities and invariants

Configuration comes from Django settings, tasks are autodiscovered, and workers acknowledge tasks only after completion.

## Complete canonical artifact

<!-- artifact: src/core/celery.py; profiles: celery-core,tasks,full -->
```python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("django_standard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-core -->
```toml
  "celery[redis]==5.6.3",
```

## Alternatives and trade-offs

Use an in-process task only for best-effort non-durable work whose loss is acceptable.

## Required tests

Run a worker smoke test and the retry/idempotency suite from the tasks recipe.

## Related standards

See [the Celery module family](../../recipes/celery/README.md) and [chat streaming](../../recipes/chat.md).
