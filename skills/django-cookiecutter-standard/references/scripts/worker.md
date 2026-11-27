# Celery Worker Entrypoint

## Purpose and when to use it

Use this entrypoint whenever `celery-core` is part of the resolved reconstruction.

## Complete canonical artifact

<!-- artifact: scripts/worker.sh; profiles: celery-core,tasks,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec celery -A core.celery:app worker \
  --loglevel="${CELERY_LOG_LEVEL:-INFO}" \
  --concurrency="${CELERY_CONCURRENCY:-2}"
```

## Responsibilities and invariants

Signals reach Celery and worker concurrency has a conservative default.

## Required tests

Check shell syntax and run the task worker smoke test.

## Related standards

See [the Celery module family](../recipes/celery/README.md) and
[the Celery beat entrypoint](beat.md).
