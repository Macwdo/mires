# Celery Postgres-Backed Job Status

## Purpose and when to use it

Use this module for a durable, queryable record of work: a `Job` row is
created before any task publishes, and PostgreSQL — not the Celery result
backend — remains the source of truth for user-visible status. Requires
`celery-core` (see [the Celery application](../../src/core/celery.md)).

## When not to use it

Do not use a Celery result backend as the product record of execution.
Results remain operational metadata; this module's `Job` row is the API
contract.

## Responsibilities and invariants

- A caller-provided idempotency key identifies one logical job per account.
- `Job.status` transitions are the durable record; `django_celery_results`
  stores Celery's own operational result data alongside it.
- Retrieval is read-only and account-scoped, matching every other tenant-owned
  resource in this handbook.

## Complete canonical artifacts

<!-- artifact: src/apps/jobs/apps.py; profiles: celery-postgres-results,tasks,full -->
```python
from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jobs"
```

<!-- artifact: src/apps/jobs/models.py; profiles: celery-postgres-results,tasks,full -->
```python
from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models

from apps.account.models import AccountOwnedModel


class Job(AccountOwnedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=80)
    idempotency_key = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=Status, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    result = models.JSONField(default=dict)
    error_code = models.CharField(max_length=80, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    objects: models.Manager[Job] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("account", "idempotency_key"),
                name="job_unique_account_idempotency",
            )
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "status", "-created_at"),
                name="job_account_status_idx",
            )
        ]
```

<!-- artifact: src/apps/jobs/serializers.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework import serializers

from apps.jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "kind",
            "status",
            "attempts",
            "result",
            "error_code",
            "created_at",
            "started_at",
            "finished_at",
        )
        read_only_fields = fields
```

<!-- artifact: src/apps/jobs/views.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer


class JobViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(account=self.request.user.account)
```

<!-- artifact: src/apps/jobs/urls.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework.routers import SimpleRouter

from apps.jobs.views import JobViewSet

app_name = "jobs"

router = SimpleRouter()
router.register("", JobViewSet, basename="job")

urlpatterns = router.urls
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-postgres-results -->
```toml
  "django-celery-results==2.6.0",
```

## Alternatives and trade-offs

Database polling is simple, observable, and reconnect-safe. Push progress
with SSE or WebSockets only when users benefit from lower latency (see
[SSE](../sse.md), [Channels](../channels.md)).

## Required tests

Test the model's account/idempotency-key uniqueness constraint, serializer
field set, and that retrieval is scoped to the requesting account.

## Related standards

See [celery-django](celery-django.md) (writes and transitions this model),
[celery-beat](celery-beat.md), and [the Celery module family](README.md).
