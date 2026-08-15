# Celery Beat — Database-Backed Scheduling

## Purpose and when to use it

Use this module when periodic work is needed on top of
[`celery-django`](celery-django.md)'s task publication. The schedule lives in
PostgreSQL (`django_celery_beat`'s `DatabaseScheduler`), not in code, so
operators can change cadence without a deploy. `sync_periodic_tasks` seeds
and updates that schedule idempotently and runs as a release step alongside
migrations. Requires `celery-django`.

## When not to use it

Do not run more than one beat process against the same schedule; duplicate
beats double-enqueue periodic tasks (enforced operationally, not by this
module).

## Responsibilities and invariants

`sync_periodic_tasks` is idempotent: running it repeatedly updates the same
`PeriodicTask` row rather than creating duplicates.

## Complete canonical artifacts

<!-- artifact: src/apps/jobs/management/commands/sync_periodic_tasks.py; profiles: celery-beat,tasks,full -->
```python
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create or update the database-backed Celery beat schedule."

    def handle(self, *args: Any, **options: Any) -> None:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )
        _, created = PeriodicTask.objects.update_or_create(
            name="purge-stale-jobs",
            defaults={
                "task": "apps.jobs.tasks.purge_stale_jobs",
                "interval": schedule,
                "crontab": None,
                "enabled": True,
            },
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(f"{verb} periodic task 'purge-stale-jobs'.")
```

<!-- artifact: src/apps/jobs/tests/test_jobs_beat.py; profiles: celery-beat,tasks,full -->
```python
import pytest
from django.core.management import call_command
from django_celery_beat.models import PeriodicTask


@pytest.mark.django_db
def test_sync_periodic_tasks_is_idempotent() -> None:
    # Act
    call_command("sync_periodic_tasks")
    call_command("sync_periodic_tasks")

    # Assert
    task = PeriodicTask.objects.get(name="purge-stale-jobs")
    assert task.task == "apps.jobs.tasks.purge_stale_jobs"
    assert task.enabled is True
    assert PeriodicTask.objects.filter(name="purge-stale-jobs").count() == 1
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-beat -->
```toml
  "django-celery-beat==2.9.0",
```

## Alternatives and trade-offs

The default file-backed `PersistentScheduler` needs a persistent volume and
loses schedule edits made outside the process. `DatabaseScheduler` trades a
small per-tick database read for operator-editable, code-free scheduling.

## Required tests

Cover retention deletion boundaries (in
[celery-django](celery-django.md)) and `sync_periodic_tasks` idempotency
(here).

## Related standards

See [celery-django](celery-django.md), [the beat entrypoint](../../scripts/beat.md),
and [the Celery module family](README.md).
