# API view foundations and probes

## Purpose and when to use it

Use these views for health probes and inherit `AccountScopedViewSet` for
account-owned resources.

## When not to use it

Global or public resources need explicit permission and query policy rather
than inheriting account scoping.

## Responsibilities and invariants

The account is derived from the authenticated user, checked for activity, and
applied before any object lookup.

## Complete canonical artifact

<!-- artifact: src/apps/api/views.py; profiles: base,full -->
```python
from typing import Any

from django.http import Http404
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.models import Account
from apps.api.health import database_is_ready
from apps.common.exceptions import AccountUnavailable


def account_for_request(request: Request) -> Account:
    account = Account.objects.filter(user=request.user).first()
    if account is None:
        raise Http404
    if not account.is_active:
        raise AccountUnavailable
    return account


class AccountScopedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_account(self) -> Account:
        return account_for_request(self.request)

    def get_queryset(self) -> Any:
        return super().get_queryset().filter(account=self.get_account())


class LivenessView(APIView):
    authentication_classes: tuple[()] = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes: tuple[()] = ()

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


class ReadinessView(APIView):
    authentication_classes: tuple[()] = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes: tuple[()] = ()

    def get(self, request: Request) -> Response:
        ready = database_is_ready()
        return Response(
            {"status": "ok" if ready else "unavailable"},
            status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
```

## Alternatives and trade-offs

Injecting account context in middleware can serve non-DRF views too, but it
makes public-route exceptions and authentication order less visible. Health
probes explicitly bypass application throttles so traffic spikes cannot turn a
healthy deployment into a failed orchestrator probe.

## Required tests

Prove account filtering occurs for list and detail actions and inactive accounts
are rejected. Test both health statuses.

## Related standards

- [Account model](../account/models.md)
- [Customer ViewSet](../customer/views.md)
