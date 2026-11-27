# Ordered Server-Sent Events

## Purpose and when to use it

Use SSE when a browser needs one-way, low-latency updates such as job progress
or assistant output. Events are persisted first, receive increasing IDs, and
can be replayed after reconnect with `Last-Event-ID`.

## When not to use it

Use ordinary polling when updates are infrequent or operational simplicity is
more important than latency. Use WebSockets when the client must send
low-latency messages on the same connection. Do not hold synchronous WSGI
workers for long-lived streams.

## Responsibilities and invariants

- The stream runs under ASGI.
- Every data event has a durable, increasing integer ID.
- Queries are account-scoped before filtering by ID.
- Reconnect starts strictly after the acknowledged `Last-Event-ID`.
- Heartbeat comments keep intermediaries from considering an idle stream dead.
- `asyncio.CancelledError` is re-raised after application cleanup.
- Reverse-proxy buffering is disabled and caching is prohibited.

## Complete canonical artifacts

SSE and Channels share the `realtime` app. The model is intentionally a small
event log, not a general message broker.

<!-- artifact: src/apps/realtime/apps.py; profiles: realtime-sse,realtime,full -->
```python
from django.apps import AppConfig


class RealtimeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.realtime"
```

<!-- artifact: src/apps/realtime/models.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

from typing import ClassVar

from django.db import models

from apps.account.models import AccountOwnedModel


class StreamEvent(AccountOwnedModel):
    id = models.BigAutoField(primary_key=True)
    topic = models.CharField(max_length=120)
    event_type = models.CharField(max_length=80)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects: models.Manager[StreamEvent] = models.Manager()

    class Meta:
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "topic", "id"),
                name="stream_account_topic_idx",
            )
        ]
        ordering = ("id",)
```

<!-- artifact: src/apps/realtime/sse.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncGenerator, Awaitable, Callable

from asgiref.sync import sync_to_async

from apps.realtime.models import StreamEvent

DisconnectHandler = Callable[[], Awaitable[None]]


async def _no_disconnect_action() -> None:
    return None


def encode_event(event: StreamEvent) -> bytes:
    data = json.dumps(event.payload, separators=(",", ":"), ensure_ascii=False)
    lines = (
        f"id: {event.pk}",
        f"event: {event.event_type}",
        f"data: {data}",
        "",
        "",
    )
    return "\n".join(lines).encode()


@sync_to_async
def _next_events(
    *,
    account_id: object,
    topic: str,
    after_id: int,
    batch_size: int,
) -> list[StreamEvent]:
    return list(
        StreamEvent.objects.filter(
            account_id=account_id,
            topic=topic,
            id__gt=after_id,
        ).order_by("id")[:batch_size]
    )


async def event_stream(
    *,
    account_id: object,
    topic: str,
    after_id: int = 0,
    poll_interval: float = 0.5,
    heartbeat_interval: float = 15.0,
    on_disconnect: DisconnectHandler = _no_disconnect_action,
) -> AsyncGenerator[bytes]:
    cursor = after_id
    last_write = time.monotonic()
    try:
        while True:
            events = await _next_events(
                account_id=account_id,
                topic=topic,
                after_id=cursor,
                batch_size=100,
            )
            if events:
                for event in events:
                    cursor = event.pk
                    last_write = time.monotonic()
                    yield encode_event(event)
                continue

            now = time.monotonic()
            if now - last_write >= heartbeat_interval:
                last_write = now
                yield b": heartbeat\n\n"
            await asyncio.sleep(poll_interval)
    except asyncio.CancelledError:
        await on_disconnect()
        raise
```

<!-- artifact: src/apps/realtime/views.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

from django.http import StreamingHttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.realtime.sse import event_stream


def parse_last_event_id(raw_value: str | None) -> int:
    if raw_value is None or raw_value == "":
        return 0
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValidationError(
            {"Last-Event-ID": "Last-Event-ID must be a non-negative integer."}
        ) from error
    if value < 0:
        raise ValidationError({"Last-Event-ID": "Last-Event-ID must be a non-negative integer."})
    return value


class EventStreamView(APIView):
    def get(self, request: Request, topic: str) -> StreamingHttpResponse:
        after_id = parse_last_event_id(request.headers.get("Last-Event-ID"))
        response = StreamingHttpResponse(
            event_stream(
                account_id=request.user.account.pk,
                topic=topic,
                after_id=after_id,
            ),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache, no-transform"
        response["X-Accel-Buffering"] = "no"
        return response
```

<!-- artifact: src/apps/realtime/urls.py; profiles: realtime-sse,realtime,full -->
```python
from django.urls import path

from apps.realtime.views import EventStreamView

app_name = "realtime"

urlpatterns = [
    path("events/<slug:topic>/", EventStreamView.as_view(), name="event-stream"),
]
```

<!-- artifact: src/apps/realtime/tests/test_sse.py; profiles: realtime-sse,realtime,full -->
```python
import asyncio
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User
from apps.realtime.models import StreamEvent
from apps.realtime.sse import event_stream
from apps.realtime.views import parse_last_event_id


@patch("apps.realtime.views.event_stream")
@pytest.mark.django_db
def test_event_stream_endpoint_sets_streaming_headers(
    stream_factory: Mock,
    api_client: APIClient,
) -> None:
    # Arrange
    user = User.objects.create_user(email="http-events@example.test")
    Account.objects.create(user=user)
    api_client.force_authenticate(user=user)
    stream_factory.return_value = iter([b"event: heartbeat\n\n"])
    url = reverse("realtime:event-stream", kwargs={"topic": "jobs"})

    # Act
    response = api_client.get(url, HTTP_LAST_EVENT_ID="7")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "text/event-stream"
    assert response["Cache-Control"] == "no-cache, no-transform"
    assert response["X-Accel-Buffering"] == "no"
    stream_factory.assert_called_once_with(
        account_id=user.account.pk,
        topic="jobs",
        after_id=7,
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_stream_replays_ordered_account_events() -> None:
    # Arrange
    user = await User.objects.acreate(email="events@example.test")
    account = await Account.objects.acreate(user=user)
    other_user = await User.objects.acreate(email="other@example.test")
    other_account = await Account.objects.acreate(user=other_user)
    first = await StreamEvent.objects.acreate(
        account=account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 10},
    )
    second = await StreamEvent.objects.acreate(
        account=account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 20},
    )
    await StreamEvent.objects.acreate(
        account=other_account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 99},
    )

    # Act
    stream = event_stream(account_id=account.pk, topic="jobs", poll_interval=0.01)
    first_chunk = await anext(stream)
    second_chunk = await anext(stream)
    await stream.aclose()

    # Assert
    assert first_chunk.startswith(f"id: {first.pk}\n".encode())
    assert second_chunk.startswith(f"id: {second.pk}\n".encode())
    assert b"99" not in first_chunk + second_chunk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_disconnect_runs_cleanup_and_propagates_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    user = await User.objects.acreate(email="cancel@example.test")
    account = await Account.objects.acreate(user=user)
    disconnected = asyncio.Event()
    clock = Mock()
    clock.monotonic.side_effect = (0.0, 61.0)
    monkeypatch.setattr("apps.realtime.sse.time", clock)

    async def cleanup() -> None:
        disconnected.set()

    stream = event_stream(
        account_id=account.pk,
        topic="idle",
        poll_interval=30,
        heartbeat_interval=60,
        on_disconnect=cleanup,
    )

    async def next_chunk() -> bytes:
        return await anext(stream)

    # Act
    heartbeat = await anext(stream)
    pending = asyncio.create_task(next_chunk())
    await asyncio.sleep(0)
    pending.cancel()

    # Assert
    with pytest.raises(asyncio.CancelledError):
        await pending
    assert heartbeat == b": heartbeat\n\n"
    assert disconnected.is_set()


def test_last_event_id_validation() -> None:
    # Arrange
    missing_cursor = None
    valid_cursor = "42"
    malformed_cursor = "not-a-number"
    negative_cursor = "-1"

    # Act
    initial_id = parse_last_event_id(missing_cursor)
    resumed_id = parse_last_event_id(valid_cursor)

    # Assert
    assert initial_id == 0
    assert resumed_id == 42
    with pytest.raises(ValidationError):
        parse_last_event_id(malformed_cursor)
    with pytest.raises(ValidationError):
        parse_last_event_id(negative_cursor)
```

## Alternatives and trade-offs

A PostgreSQL event table makes replay deterministic but needs retention and
index maintenance. Redis Streams can provide replay at higher throughput but
introduce another durable cursor and tenant-scoping boundary. Plain pub/sub
has low latency but loses messages during disconnects, so clients still need a
database snapshot or recovery endpoint.

## Required tests

Test response content type and proxy headers, ordered replay, account
isolation, malformed cursors, batches larger than 100, heartbeat timing,
disconnect cleanup, retention boundaries, slow clients, and application
shutdown. Run a smoke test with Daphne and a proxy configured exactly like
production.

## Related standards

- [Channels](channels.md)
- [Celery module family](celery/README.md)
- [Chat streaming](chat.md)
- [Deployment](deployment.md)
- [API design](../docs/api-design.md)
