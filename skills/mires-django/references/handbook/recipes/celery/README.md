# Celery

Durable background work, split into composable modules along the same
edges [`docs/reconstruction.md`](../../docs/reconstruction.md) resolves:

- [`celery-postgres-results`](celery-postgres-results.md) — the durable
  `Job` model, its read-only DRF API, and `django-celery-results`. Requires
  only `celery-core` (the project Celery app at
  [`src/core/celery.md`](../../src/core/celery.md)).
- [`celery-django`](celery-django.md) — task publication and status
  transitions (`create_job`, `claim_job`, `run_job`). Requires
  `celery-postgres-results`, because every operation reads or writes the
  `Job` row that module owns.
- [`celery-beat`](celery-beat.md) — database-backed periodic scheduling
  (`sync_periodic_tasks`, `DatabaseScheduler`). Requires `celery-django`.
- [`celery-redis-broker`](celery-redis-broker.md) — broker/result-backend
  configuration notes. Requires only `celery-core`; owns no artifacts of its
  own because the broker settings are aggregator-owned (see
  [settings](../../src/core/settings/README.md), [environment](../../environment.md)).

Requesting `celery-django` alone pulls in `celery-postgres-results`
transitively (and `celery-core` through it) but not `celery-beat` — no
periodic scheduling is materialized unless asked for. The legacy `tasks`
alias still resolves to all five.

## Related standards

See [the Celery application](../../src/core/celery.md),
[the worker entrypoint](../../scripts/worker.md),
[the beat entrypoint](../../scripts/beat.md), and
[chat streaming](../chat.md), which uses `celery-core` directly without any
of these Job-model-backed modules.
