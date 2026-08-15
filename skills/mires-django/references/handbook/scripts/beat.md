# Celery Beat Entrypoint

## Purpose and when to use it

Use this entrypoint whenever `celery-beat` is part of the resolved
reconstruction, alongside at least one worker. Beat itself never executes
task bodies; it only enqueues due tasks read from the database-backed
schedule described in [celery-beat](../recipes/celery/celery-beat.md).

## When not to use it

Do not run more than one beat process against the same schedule; duplicate
beats double-enqueue periodic tasks. `DatabaseScheduler` polls PostgreSQL, not
a file, so no `celerybeat-schedule` file needs a shared volume.

## Complete canonical artifact

<!-- artifact: scripts/beat.sh; profiles: celery-beat,tasks,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec celery -A core.celery:app beat \
  --loglevel="${CELERY_LOG_LEVEL:-INFO}" \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Responsibilities and invariants

Signals reach Celery. The scheduler is always `DatabaseScheduler`, so a
schedule change only requires updating `PeriodicTask` rows, not a redeploy.

## Alternatives and trade-offs

The default file-backed `PersistentScheduler` needs a persistent volume and
loses schedule edits made outside the process. `DatabaseScheduler` trades a
small per-tick database read for operator-editable, code-free scheduling.

## Required tests

Check shell syntax and run the `sync_periodic_tasks` idempotency test from
[celery-beat](../recipes/celery/celery-beat.md).

## Related standards

See [the Celery module family](../recipes/celery/README.md) and
[the Celery worker entrypoint](worker.md).
