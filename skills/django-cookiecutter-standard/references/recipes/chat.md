# Chat Streaming over Celery, Redis Streams, and SSE

## Purpose and when to use it

Use this transport when a browser needs to watch a multi-turn assistant
conversation stream token-by-token without holding a synchronous worker for
the duration of the agent turn. The HTTP request that starts a turn returns
immediately after enqueuing a Celery task; the task runs the agent and relays
every event onto a per-thread Redis Stream; an async SSE view tails that
stream and forwards events to the browser as they arrive. The SSE view never
reads the Celery result backend — it only ever reads Redis — so a terminal
event MUST be published on every code path, including failures, or a client
would hang until its own timeout.

This recipe assumes [OpenAI and Deep Agents](openai-deep-agents.md) supplies
`ChatService`, `ChatStreamEvent`, and `get_thread_id`. It is deliberately
narrower than [ordered SSE](sse.md): chat events are ephemeral relay traffic
scoped to one in-flight turn, not a durable, replayable, account-scoped event
log, so a Redis Stream with a short TTL is enough and a PostgreSQL-backed
model would be unused overhead.

## When not to use it

Use a direct synchronous call to `ChatService.chat` when the product can wait
for one HTTP response and does not need incremental tokens. Use
[ordered SSE](sse.md) instead when clients must reconnect after minutes or
hours and replay history from a durable cursor — Redis Streams here expire
with the turn and are not a long-term record. Use [Channels](channels.md)
instead when the browser must also send low-latency messages on the same
connection, such as interrupting a running agent turn.

## Responsibilities and invariants

- `ChatStartAPIView` only enqueues a task; it never runs the agent inline.
- The Celery task publishes every `ChatStreamEvent` the agent produces, in
  order, to `chat:stream:<thread_id>`.
- The task publishes a terminal `error` event on every failure path —
  guardrail rejection and unexpected exceptions alike — so the SSE view
  always reaches a stopping point instead of blocking until its own timeout.
- The stream key gets a TTL in a `finally` block so abandoned or completed
  streams are reclaimed regardless of outcome.
- The SSE view runs under ASGI, reads with a blocking `XREAD` cursor, and
  stops as soon as it forwards a `complete` or `error` event.
- The SSE view enforces its own wall-clock timeout independent of the
  gunicorn/ASGI worker timeout, and the deployed worker timeout stays
  comfortably above it so the platform never kills the connection first.
- A periodic heartbeat is unnecessary here because `XREAD` with `block`
  already bounds how long the view can be idle before re-checking its own
  deadline; do not add polling sleeps on top of the blocking read.
- History and message content are never logged.

## Complete canonical artifacts

<!-- artifact: src/apps/chat/apps.py; profiles: chat-streaming,vector-ai,full -->
```python
from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
```

<!-- artifact: src/apps/chat/redis.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import redis
import redis.asyncio as aredis
from django.conf import settings

if TYPE_CHECKING:
    from apps.assistants.types import ChatStreamEvent

_sync_client: redis.Redis | None = None


def stream_key(thread_id: str) -> str:
    """Return the Redis Stream key that relays chat events for one thread."""
    return f"chat:stream:{thread_id}"


def get_sync_redis_client() -> redis.Redis:
    """Return a process-wide sync Redis client, used by the Celery worker."""
    global _sync_client
    if _sync_client is None:
        _sync_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _sync_client


def get_async_redis_client() -> aredis.Redis:
    """Return a new async Redis client bound to the caller's event loop, used by the SSE view."""
    return aredis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_event(client: redis.Redis, *, thread_id: str, event: ChatStreamEvent) -> str:
    """Append one chat stream event to the thread's Redis Stream."""
    return client.xadd(stream_key(thread_id), {"event": json.dumps(event)})


def expire_stream(client: redis.Redis, *, thread_id: str, ttl_seconds: int) -> None:
    """Set a TTL on the thread's stream so finished or abandoned streams get cleaned up."""
    client.expire(stream_key(thread_id), ttl_seconds)


def decode_entry(fields: dict[str, str]) -> ChatStreamEvent:
    """Decode a raw Redis Stream entry's fields back into a ChatStreamEvent."""
    return json.loads(fields["event"])
```

<!-- artifact: src/apps/chat/tasks.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings

from apps.assistants.chat import ChatService
from apps.assistants.types import ChatMessage
from apps.chat.redis import expire_stream, get_sync_redis_client, publish_event

logger = logging.getLogger(__name__)


@shared_task
def run_chat_stream_task(*, thread_id: str, message: str, history: list[ChatMessage] | None = None) -> None:
    """Run one chat turn and relay every streamed event to the thread's Redis Stream.

    The SSE view only ever reads from Redis, never from this task's Celery result, so a
    terminal "error" event MUST be published on every failure path or the SSE client would
    hang until its own timeout instead of failing fast.
    """
    client = get_sync_redis_client()
    try:
        for event in ChatService().stream(message, history):
            publish_event(client, thread_id=thread_id, event=event)

    except (ValueError, RuntimeError) as exc:
        logger.warning("Chat guardrail rejected thread %s: %s", thread_id, exc)
        publish_event(client, thread_id=thread_id, event={"type": "error", "agent": None, "message": str(exc)})

    except Exception:
        logger.exception("Unhandled error streaming chat for thread %s", thread_id)
        publish_event(
            client,
            thread_id=thread_id,
            event={"type": "error", "agent": None, "message": "Something went wrong while generating the response."},
        )
    finally:
        expire_stream(client, thread_id=thread_id, ttl_seconds=settings.CHAT_STREAM_TTL_SECONDS)
```

`CHAT_STREAM_TTL_SECONDS` is a small setting owned by this recipe when
enabled; set it comfortably above the SSE view's `max_wait_seconds` so a slow
consumer can still read the last events before Redis reclaims the key.

<!-- artifact: src/apps/chat/serializers.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()


class ChatStartSerializerRequest(serializers.Serializer):
    message = serializers.CharField(allow_blank=False)
    thread_id = serializers.CharField(required=False, allow_null=True, default=None)
    history = ChatMessageSerializer(many=True, required=False, default=list)


class ChatStartSerializerResponse(serializers.Serializer):
    thread_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
```

<!-- artifact: src/apps/chat/views.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator

from django.http import HttpRequest, StreamingHttpResponse
from django.views import View
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistants.chat import get_thread_id
from apps.assistants.types import ChatStreamEvent
from apps.chat.redis import decode_entry, get_async_redis_client, stream_key
from apps.chat.serializers import ChatStartSerializerRequest, ChatStartSerializerResponse
from apps.chat.tasks import run_chat_stream_task


class ChatStartAPIView(APIView):
    def post(self, request: Request) -> Response:
        input_serializer = ChatStartSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            thread_id = get_thread_id(data["thread_id"])
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

        run_chat_stream_task.delay(thread_id=thread_id, message=data["message"], history=data["history"])

        output_serializer = ChatStartSerializerResponse({"thread_id": thread_id, "status": "accepted"})
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)


class ChatStreamAPIView(View):
    """Relay a thread's Redis Stream to the browser as Server-Sent Events.

    The deployed worker timeout must stay comfortably above `max_wait_seconds`,
    otherwise the platform kills the worker process mid-stream before this view's own
    timeout logic gets a chance to close the connection gracefully.
    """

    max_wait_seconds = 120
    read_block_ms = 15_000

    async def get(self, _request: HttpRequest, thread_id: str) -> StreamingHttpResponse:
        response = StreamingHttpResponse(
            self._event_source(thread_id),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        response["Connection"] = "keep-alive"
        return response

    async def _event_source(self, thread_id: str) -> AsyncIterator[bytes]:
        client = get_async_redis_client()
        key = stream_key(thread_id)
        last_id = "0"
        deadline = time.monotonic() + self.max_wait_seconds
        try:
            while True:
                if time.monotonic() > deadline:
                    yield self._sse_format({"type": "error", "agent": None, "message": "Stream timed out."})
                    return

                result = await client.xread({key: last_id}, count=50, block=self.read_block_ms)
                if not result:
                    continue

                for _stream_name, entries in result:
                    for entry_id, fields in entries:
                        last_id = entry_id
                        event = decode_entry(fields)
                        yield self._sse_format(event)
                        if event["type"] in ("complete", "error"):
                            return
        finally:
            await client.aclose()

    @staticmethod
    def _sse_format(event: ChatStreamEvent) -> bytes:
        return f"data: {json.dumps(event)}\n\n".encode()
```

`ChatStartAPIView` inherits the project's default authentication and
permission classes; scope the enqueued thread to `request.user` (for example
by prefixing `stream_key` with the account id) whenever chat history is
account-owned rather than anonymous.

<!-- artifact: src/apps/chat/urls.py; profiles: chat-streaming,vector-ai,full -->
```python
from django.urls import path

from apps.chat.views import ChatStartAPIView, ChatStreamAPIView

app_name = "chat"

urlpatterns = [
    path("chat", ChatStartAPIView.as_view(), name="chat-start"),
    path("chat/<str:thread_id>/events", ChatStreamAPIView.as_view(), name="chat-stream"),
]
```

<!-- artifact: src/apps/chat/tests/test_chat_start_api.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@patch("apps.chat.views.run_chat_stream_task")
def test_start_enqueues_a_task_and_returns_a_thread_id(
    task: object,
    api_client: APIClient,
) -> None:
    # Act
    response = api_client.post(
        reverse("chat:chat-start"),
        {"message": "Hi there"},
        format="json",
    )

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["status"] == "accepted"
    assert response.data["thread_id"]
    task.delay.assert_called_once_with(
        thread_id=response.data["thread_id"],
        message="Hi there",
        history=[],
    )


def test_start_rejects_a_blank_message(api_client: APIClient) -> None:
    # Act
    response = api_client.post(reverse("chat:chat-start"), {"message": ""}, format="json")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("apps.chat.views.run_chat_stream_task")
def test_start_rejects_a_blank_thread_id(task: object, api_client: APIClient) -> None:
    # Act
    response = api_client.post(
        reverse("chat:chat-start"),
        {"message": "Hi", "thread_id": "   "},
        format="json",
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    task.delay.assert_not_called()
```

<!-- artifact: src/apps/chat/tests/test_chat_stream_view.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import AsyncMock

import pytest
from django.urls import reverse

from apps.chat.views import ChatStreamAPIView


@pytest.mark.asyncio
async def test_event_source_forwards_events_and_stops_at_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    client = AsyncMock()
    client.xread.side_effect = [
        [("chat:stream:t1", [("1-0", {"event": '{"type": "token", "agent": "assistant", "content": "Hi"}'})])],
        [("chat:stream:t1", [("2-0", {"event": '{"type": "complete", "history": []}'})])],
    ]
    monkeypatch.setattr("apps.chat.views.get_async_redis_client", lambda: client)
    view = ChatStreamAPIView()

    # Act
    chunks = [chunk async for chunk in view._event_source("t1")]

    # Assert
    assert b'"type": "token"' in chunks[0] or b'"type":"token"' in chunks[0].replace(b" ", b"")
    assert b"complete" in chunks[-1]
    client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_source_times_out_when_nothing_is_published(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    client = AsyncMock()
    client.xread.return_value = []
    monkeypatch.setattr("apps.chat.views.get_async_redis_client", lambda: client)
    clock = iter([0.0, 0.0, 200.0])
    monkeypatch.setattr("apps.chat.views.time.monotonic", lambda: next(clock))
    view = ChatStreamAPIView()
    view.max_wait_seconds = 1

    # Act
    chunks = [chunk async for chunk in view._event_source("t1")]

    # Assert
    assert b"timed out" in chunks[-1]
    client.aclose.assert_awaited_once()


def test_stream_url_routes_to_the_thread(client: object) -> None:
    # Assert
    assert reverse("chat:chat-stream", kwargs={"thread_id": "abc"}) == "/chat/abc/events"
```

<!-- artifact: src/apps/chat/tests/test_redis_helpers.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import Mock

from apps.chat.redis import decode_entry, expire_stream, publish_event, stream_key


def test_stream_key_is_namespaced_per_thread() -> None:
    # Assert
    assert stream_key("abc-123") == "chat:stream:abc-123"


def test_publish_event_serializes_json_onto_the_stream() -> None:
    # Arrange
    client = Mock()
    event = {"type": "token", "agent": "assistant", "content": "Hi"}

    # Act
    publish_event(client, thread_id="t1", event=event)

    # Assert
    client.xadd.assert_called_once()
    args, kwargs = client.xadd.call_args
    assert args[0] == "chat:stream:t1"
    assert decode_entry(args[1]) == event


def test_expire_stream_sets_the_configured_ttl() -> None:
    # Arrange
    client = Mock()

    # Act
    expire_stream(client, thread_id="t1", ttl_seconds=300)

    # Assert
    client.expire.assert_called_once_with("chat:stream:t1", 300)
```

<!-- dependency-fragment: pyproject.toml#dev; modules: chat-streaming -->
```toml
  "pytest-asyncio==1.4.0",
```

<!-- dependency-fragment: pyproject.toml#pytest; modules: chat-streaming -->
```toml
asyncio_mode = "auto"
```

## Alternatives and trade-offs

Streaming the agent's response directly from a synchronous ASGI view avoids
Celery and Redis entirely, but ties the response to one HTTP connection: a
client refresh loses the in-flight turn, and a single slow agent call occupies
an ASGI worker for its full duration. Relaying through a Celery task and a
Redis Stream decouples turn execution from the viewer's connection — the
worker can retry or run independently of the browser, and any number of tabs
could tail the same `thread_id`. The trade-off is two extra hops and a second
place (Redis) where "what happened during this turn" briefly lives; the TTL
keeps that window short and cheap rather than promoting it to a durable
record. Reach for [ordered SSE](sse.md)'s PostgreSQL-backed model instead when
a durable, replayable transcript is itself a product requirement.

## Required tests

Cover the start endpoint's enqueue and validation paths, the SSE view's event
forwarding, timeout, and cleanup, and the Redis helpers' key namespacing and
serialization. Run one integration test with a real Celery worker (eager mode
disabled) and a real Redis instance driving the full task through the SSE
view, confirming a terminal event is always published, including when the
agent raises.

## Related standards

- [OpenAI and Deep Agents](openai-deep-agents.md)
- [Celery module family](celery/README.md)
- [SSE](sse.md)
- [Channels](channels.md)
- [Testing](../docs/testing.md)
