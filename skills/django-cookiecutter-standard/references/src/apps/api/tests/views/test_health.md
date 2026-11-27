# Health endpoint tests

## Purpose and when to use it

Verify public liveness and database-aware readiness behavior.

## When not to use it

These unit tests do not replace a deployed probe smoke test.

## Responsibilities and invariants

Liveness is always dependency-free; readiness returns 503 when the database
check fails.

## Complete canonical artifact

<!-- artifact: src/apps/api/tests/views/test_health.py; profiles: base,full -->
```python
from unittest.mock import MagicMock, patch

from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def test_liveness_is_public(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:live")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    assert response["X-Request-ID"]


@patch("apps.api.health.connection.cursor")
def test_readiness_returns_ok_when_database_is_ready(
    cursor_factory: MagicMock,
    api_client: APIClient,
) -> None:
    # Arrange
    url = reverse("api:ready")
    cursor = cursor_factory.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1,)

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    cursor.execute.assert_called_once_with("SELECT 1")


@patch("apps.api.health.connection.cursor", side_effect=DatabaseError)
def test_readiness_returns_503_when_database_is_unavailable(
    cursor_factory: MagicMock,
    api_client: APIClient,
) -> None:
    # Arrange
    url = reverse("api:ready")

    # Act
    response = api_client.get(
        url,
        HTTP_X_REQUEST_ID="gateway-request-42",
    )

    # Assert
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"status": "unavailable"}
    assert response["X-Request-ID"] == "gateway-request-42"
    cursor_factory.assert_called_once_with()
```

## Alternatives and trade-offs

Integration tests against PostgreSQL catch driver and credential failures; unit
tests make success and outage branches deterministic.

## Required tests

Run both unit tests and a deployed readiness probe.

## Related standards

- [Health implementation](../../health.md)
- [Request ID middleware](../../middleware.md)
