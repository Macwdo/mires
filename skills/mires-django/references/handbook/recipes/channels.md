# Channels and Daphne WebSockets

## Purpose and when to use it

Use Channels when clients need bidirectional, long-lived communication or
server-pushed account events over WebSockets. Daphne serves the ASGI
application, Redis carries group messages between processes, and PostgreSQL
provides reconnect replay.

## When not to use it

Use REST for request-response operations and SSE for one-way browser streams.
Do not put authorization only in the connection URL, trust `Origin`, or assume
Redis group delivery is durable.

## Responsibilities and invariants

- `ProtocolTypeRouter` keeps ordinary Django HTTP and WebSockets explicit.
- `AllowedHostsOriginValidator` rejects untrusted browser origins.
- Authentication is resolved before the consumer accepts the socket.
- Every subscription verifies account ownership.
- Group names are derived from validated server-side identifiers.
- Persisted event IDs support reconnect; Redis only reduces delivery latency.
- Clients reconnect with bounded exponential backoff and their last event ID.

## Complete canonical artifacts

The middleware accepts the same short-lived JWT used by the REST API in the
`Authorization: Bearer` handshake header. Browsers that cannot set handshake
headers should exchange their authenticated session for a short-lived,
single-purpose socket ticket over HTTPS rather than placing a long-lived token
in the query string.

<!-- artifact: src/apps/realtime/auth.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.authentication.models import User

ASGIApp = Callable[
    [
        dict[str, Any],
        Callable[[], Awaitable[dict[str, Any]]],
        Callable[[dict[str, Any]], Awaitable[None]],
    ],
    Awaitable[None],
]


def _bearer_token(headers: list[tuple[bytes, bytes]]) -> str | None:
    authorization = next(
        (value for name, value in headers if name.lower() == b"authorization"),
        b"",
    )
    scheme, separator, token = authorization.partition(b" ")
    if separator == b"" or scheme.lower() != b"bearer":
        return None
    try:
        return token.decode("ascii")
    except UnicodeDecodeError:
        return None


async def _authenticate(headers: list[tuple[bytes, bytes]]) -> User | AnonymousUser:
    encoded = _bearer_token(headers)
    if encoded is None:
        return AnonymousUser()
    try:
        token = AccessToken(
            encoded  # ty: ignore[invalid-argument-type]  # SimpleJWT accepts encoded text at runtime.
        )
        user_id = token["user_id"]
        return await User.objects.aget(pk=user_id, is_active=True)
    except KeyError, ObjectDoesNotExist, TokenError:
        return AnonymousUser()


class JwtAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        authenticated_scope = dict(scope)
        authenticated_scope["user"] = await _authenticate(scope.get("headers", []))
        await self.app(authenticated_scope, receive, send)
```

<!-- artifact: src/apps/realtime/consumers.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.account.models import Account
from apps.realtime.models import StreamEvent


class AccountEventConsumer(AsyncJsonWebsocketConsumer):
    group_name: str
    account_id: str

    async def connect(self) -> None:
        user = self.scope["user"]
        self.account_id = str(self.scope["url_route"]["kwargs"]["account_id"])
        account_is_allowed = (
            user.is_authenticated
            and await Account.objects.filter(
                pk=self.account_id,
                user=user,
                is_active=True,
            ).aexists()
        )
        if not account_is_allowed:
            await self.close(code=4403)
            return

        self.group_name = f"account.{self.account_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        raw_after = parse_qs(self.scope.get("query_string", b"").decode("ascii")).get(
            "after", ["0"]
        )[0]
        try:
            after_id = max(0, int(raw_after))
        except ValueError:
            await self.close(code=4400)
            return

        events = StreamEvent.objects.filter(
            account_id=self.account_id,
            id__gt=after_id,
        ).order_by("id")
        async for event in events.aiterator(chunk_size=100):
            await self.send_json(
                {
                    "id": event.pk,
                    "topic": event.topic,
                    "type": event.event_type,
                    "payload": event.payload,
                }
            )

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def account_event(self, event: dict[str, object]) -> None:
        await self.send_json(event["message"])
```

<!-- artifact: src/apps/realtime/publish.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from apps.account.models import Account
from apps.realtime.models import StreamEvent


@transaction.atomic
def publish_account_event(
    *,
    account: Account,
    topic: str,
    event_type: str,
    payload: dict[str, object],
) -> StreamEvent:
    event = StreamEvent.objects.create(
        account=account,
        topic=topic,
        event_type=event_type,
        payload=payload,
    )

    def notify() -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            f"account.{account.pk}",
            {
                "type": "account.event",
                "message": {
                    "id": event.pk,
                    "topic": event.topic,
                    "type": event.event_type,
                    "payload": event.payload,
                },
            },
        )

    transaction.on_commit(notify)
    return event
```

<!-- artifact: src/apps/realtime/routing.py; profiles: realtime-channels,realtime,full -->
```python
from django.urls import path

from apps.realtime.consumers import AccountEventConsumer

websocket_urlpatterns = [
    path(
        "ws/accounts/<int:account_id>/events/",
        AccountEventConsumer.as_asgi(),
    )
]
```

This complete application artifact can be used directly with
`daphne apps.realtime.application:application`. The central core ASGI standard
may expose the same composition when `realtime` is selected.

<!-- artifact: src/apps/realtime/application.py; profiles: realtime-channels,realtime,full -->
```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.realtime.auth import JwtAuthMiddleware
from apps.realtime.routing import websocket_urlpatterns

django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                JwtAuthMiddleware(
                    URLRouter(websocket_urlpatterns),
                )
            )
        ),
    }
)
```

<!-- artifact: src/apps/realtime/tests/test_websocket.py; profiles: realtime-channels,realtime,full -->
```python
import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from rest_framework_simplejwt.tokens import AccessToken

from apps.account.models import Account
from apps.authentication.models import User
from apps.realtime.application import application


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_authenticated_socket_receives_group_event() -> None:
    # Arrange
    user = await User.objects.acreate(email="socket@example.test")
    account = await Account.objects.acreate(user=user)
    token = AccessToken.for_user(user)
    communicator = WebsocketCommunicator(
        application,
        f"/ws/accounts/{account.pk}/events/?after=0",
        headers=[
            (b"host", b"localhost"),
            (b"origin", b"http://localhost"),
            (b"authorization", f"Bearer {token}".encode()),
        ],
    )
    channel_layer = get_channel_layer()
    if channel_layer is None:
        raise RuntimeError("Channel layer is not configured.")

    # Act
    connected, _subprotocol = await communicator.connect()
    await channel_layer.group_send(
        f"account.{account.pk}",
        {
            "type": "account.event",
            "message": {
                "id": 1,
                "topic": "jobs",
                "type": "progress",
                "payload": {"percent": 50},
            },
        },
    )
    message = await communicator.receive_json_from()
    await communicator.disconnect()

    # Assert
    assert connected is True
    assert message == {
        "id": 1,
        "topic": "jobs",
        "type": "progress",
        "payload": {"percent": 50},
    }


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_untrusted_origin_is_rejected() -> None:
    # Arrange
    communicator = WebsocketCommunicator(
        application,
        "/ws/accounts/1/events/",
        headers=[
            (b"host", b"testserver"),
            (b"origin", b"https://untrusted.example.test"),
        ],
    )

    # Act
    connected, _subprotocol = await communicator.connect()

    # Assert
    assert connected is False
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: realtime-channels -->
```toml
  "channels==4.3.2",
  "channels-redis==4.3.0",
  "daphne==4.2.3",
```

<!-- dependency-fragment: pyproject.toml#dev; modules: realtime-channels -->
```toml
  "pytest-asyncio==1.4.0",
  "websockets==15.0.1",
```

<!-- dependency-fragment: pyproject.toml#pytest; modules: realtime-channels -->
```toml
asyncio_mode = "auto"
```

## Alternatives and trade-offs

Running all HTTP under Daphne simplifies one deployment and supports SSE and
WebSockets. Splitting WSGI REST and ASGI realtime services can isolate scaling
and failure modes but requires shared authentication, deployment, and routing
configuration. Redis groups are ephemeral; the event table provides recovery.

## Required tests

Test missing, expired, and malformed tokens; foreign accounts; inactive users;
untrusted and absent origins; replay after reconnect; Redis group delivery;
disconnect cleanup; backpressure; and worker restart. Use
`WebsocketCommunicator` for protocol behavior and smoke-test Daphne with Redis
in the integration environment.

## Related standards

- [SSE](sse.md)
- [Deployment](deployment.md)
- [Security](../docs/security.md)
- [Operations](../docs/operations.md)
