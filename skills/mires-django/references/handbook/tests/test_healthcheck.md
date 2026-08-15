# Live Health Smoke Test

## Purpose and when to use it

This optional system test checks a process already running through its public HTTP boundary.

## When not to use it

The ordinary unit suite uses Django's test client and requires no live process.

## Complete canonical artifact

<!-- artifact: tests/test_healthcheck.py; profiles: base -->
```python
import urllib.request

import pytest


@pytest.mark.integration
def test_live_health_endpoint(live_server_url: str) -> None:
    # Arrange
    url = f"{live_server_url}/api/v1/live/"

    # Act
    with urllib.request.urlopen(
        url,
        timeout=3,
    ) as response:
        status_code = response.status
        content_type = response.headers["Content-Type"]

    # Assert
    assert status_code == 200
    assert content_type.startswith("application/json")
```

## Required tests

Run this test only after the chosen WSGI or ASGI server reports ready.
