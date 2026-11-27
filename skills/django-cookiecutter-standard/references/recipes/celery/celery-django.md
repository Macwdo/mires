# Celery Task Publication and Status Transitions

## Purpose and when to use it

Use this module when work must survive a web request, run on a schedule, or
retry after a transient dependency failure. It publishes and executes the
Celery task that drives a [`celery-postgres-results`](celery-postgres-results.md)
`Job` through its status transitions. Requires `celery-postgres-results`.

## When not to use it

Do not enqueue work that must commit atomically inside the current request.
Use `transaction.on_commit` when a task depends on newly committed rows. Do
not retry validation or authorization failures.

## Responsibilities and invariants

- Task publication happens only after the creating transaction commits.
- Workers claim a pending job with a row lock.
- Retriable failures return the job to `pending`; terminal failures are
  recorded without leaking secrets.
- Celery retries and task redelivery may run the same task more than once,
  so effects use their own durable idempotency key.
- Account-scoped periodic jobs are created through the same service used by
  request handlers. System-wide maintenance tasks, such as retention
  sweeps, may run directly since they have no owning account.

## Complete canonical artifacts

<!-- artifact: src/apps/jobs/services.py; profiles: celery-django,tasks,full -->
```python
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.account.models import Account
from apps.jobs.models import Job


@transaction.atomic
def create_job(
    *,
    account: Account,
    kind: str,
    idempotency_key: str,
    enqueue: Callable[[str], Any],
) -> tuple[Job, bool]:
    job, created = Job.objects.get_or_create(
        account=account,
        idempotency_key=idempotency_key,
        defaults={"kind": kind},
    )
    if created:
        transaction.on_commit(lambda: enqueue(str(job.pk)))
    return job, created


@transaction.atomic
def claim_job(*, job_id: str) -> Job | None:
    job = Job.objects.select_for_update().filter(pk=job_id).first()
    if job is None or job.status != Job.Status.PENDING:
        return None
    job.status = Job.Status.RUNNING
    job.attempts += 1
    job.started_at = timezone.now()
    job.error_code = ""
    job.save(update_fields=("status", "attempts", "started_at", "error_code", "updated_at"))
    return job


@transaction.atomic
def mark_job_succeeded(*, job_id: str, result: dict[str, object]) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(
        status=Job.Status.SUCCEEDED,
        result=result,
        finished_at=timezone.now(),
        error_code="",
    )


@transaction.atomic
def mark_job_pending_for_retry(*, job_id: str) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(status=Job.Status.PENDING, error_code="temporary_dependency_failure")


@transaction.atomic
def mark_job_failed(*, job_id: str, error_code: str) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(
        status=Job.Status.FAILED,
        error_code=error_code,
        finished_at=timezone.now(),
    )


def purge_finished_jobs(*, older_than: timedelta) -> int:
    cutoff = timezone.now() - older_than
    deleted, _ = Job.objects.filter(
        status__in=(Job.Status.SUCCEEDED, Job.Status.FAILED),
        finished_at__lt=cutoff,
    ).delete()
    return deleted
```

<!-- artifact: src/apps/jobs/tasks.py; profiles: celery-django,tasks,full -->
```python
from __future__ import annotations

from datetime import timedelta
from typing import Any

import httpx
from celery import shared_task

from apps.jobs.services import (
    claim_job,
    mark_job_failed,
    mark_job_pending_for_retry,
    mark_job_succeeded,
    purge_finished_jobs,
)


def perform_job_effect(*, job_id: str) -> dict[str, object]:
    return {"job_id": job_id, "processed": True}


@shared_task(
    bind=True,
    autoretry_for=(),
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=5,
)
def run_job(self: Any, job_id: str) -> None:
    job = claim_job(job_id=job_id)
    if job is None:
        return

    try:
        result = perform_job_effect(job_id=str(job.pk))
    except (httpx.TimeoutException, httpx.NetworkError) as error:
        mark_job_pending_for_retry(job_id=str(job.pk))
        countdown = min(300, 2**job.attempts)
        raise self.retry(exc=error, countdown=countdown) from error
    except Exception:
        mark_job_failed(job_id=str(job.pk), error_code="job_execution_failed")
        raise
    else:
        mark_job_succeeded(job_id=str(job.pk), result=result)


@shared_task
def purge_stale_jobs() -> int:
    return purge_finished_jobs(older_than=timedelta(days=30))
```

<!-- artifact: src/apps/jobs/tests/test_jobs.py; profiles: celery-django,tasks,full -->
```python
from datetime import timedelta

import pytest
from celery.exceptions import Retry
from django.db import transaction
from django.utils import timezone

from apps.account.models import Account
from apps.authentication.models import User
from apps.jobs.models import Job
from apps.jobs.services import create_job, purge_finished_jobs
from apps.jobs.tasks import purge_stale_jobs, run_job


@pytest.mark.django_db(transaction=True)
def test_create_job_is_idempotent_and_publishes_after_commit() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    published: list[str] = []

    # Act
    with transaction.atomic():
        first, first_created = create_job(
            account=account,
            kind="customer-export",
            idempotency_key="export-2026-07",
            enqueue=published.append,
        )
        second, second_created = create_job(
            account=account,
            kind="customer-export",
            idempotency_key="export-2026-07",
            enqueue=published.append,
        )
        published_before_commit = list(published)

    # Assert
    assert published_before_commit == []
    assert first == second
    assert first_created is True
    assert second_created is False
    assert published == [str(first.pk)]


@pytest.mark.django_db
def test_completed_task_is_safe_to_redeliver() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    job = Job.objects.create(
        account=account,
        kind="customer-export",
        idempotency_key="one-delivery",
    )

    # Act
    run_job.run(str(job.pk))
    run_job.run(str(job.pk))
    job.refresh_from_db()

    # Assert
    assert job.status == Job.Status.SUCCEEDED
    assert job.attempts == 1


@pytest.mark.django_db
def test_transient_failure_returns_job_to_pending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    job = Job.objects.create(account=account, kind="sync", idempotency_key="retry")

    def fail(*, job_id: str) -> dict[str, object]:
        import httpx

        raise httpx.ConnectError("temporary")

    monkeypatch.setattr("apps.jobs.tasks.perform_job_effect", fail)

    # Assert
    with pytest.raises(Retry):
        run_job.apply(args=(str(job.pk),), throw=True)
    assert (persisted_job := Job.objects.get(pk=job.pk)).status == Job.Status.PENDING
    assert persisted_job.error_code == "temporary_dependency_failure"


@pytest.mark.django_db
def test_purge_stale_jobs_deletes_only_old_terminal_jobs() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    stale = Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="stale",
        status=Job.Status.SUCCEEDED,
        finished_at=timezone.now() - timedelta(days=31),
    )
    recent = Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="recent",
        status=Job.Status.SUCCEEDED,
        finished_at=timezone.now(),
    )
    pending = Job.objects.create(account=account, kind="export", idempotency_key="pending")

    # Act
    deleted = purge_stale_jobs.run()

    # Assert
    assert deleted == 1
    assert not Job.objects.filter(pk=stale.pk).exists()
    assert Job.objects.filter(pk=recent.pk).exists()
    assert Job.objects.filter(pk=pending.pk).exists()


@pytest.mark.django_db
def test_purge_finished_jobs_returns_deleted_count() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="stale",
        status=Job.Status.FAILED,
        finished_at=timezone.now() - timedelta(days=60),
    )

    # Act
    deleted = purge_finished_jobs(older_than=timedelta(days=30))

    # Assert
    assert deleted == 1
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-django -->
```toml
  "httpx==0.28.1",
```

## Alternatives and trade-offs

A database-backed task queue reduces infrastructure but has a different
throughput and scheduling profile than Celery/Redis.

## Required tests

Run a worker against Redis and PostgreSQL. Cover transaction rollback
without publication, duplicate HTTP requests, worker redelivery, retry
exhaustion, terminal failure sanitization, account-scoped polling, and
result expiration. Run worker tests with eager mode disabled for at least
one integration suite.

## Related standards

See [celery-postgres-results](celery-postgres-results.md) (owns the `Job`
model this module transitions), [celery-beat](celery-beat.md), and
[the Celery module family](README.md).
