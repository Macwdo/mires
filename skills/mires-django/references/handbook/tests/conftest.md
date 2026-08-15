# System Test Fixtures

## Purpose and when to use it

System tests consume a running server URL explicitly; they never start infrastructure during import.

## Complete canonical artifact

<!-- artifact: tests/conftest.py; profiles: base -->
```python
import os

import pytest


@pytest.fixture(scope="session")
def live_server_url() -> str:
    configured = os.getenv("LIVE_SERVER_URL")
    if not configured:
        pytest.skip("LIVE_SERVER_URL is required for live-server smoke tests")
    return configured.rstrip("/")
```

## Required tests

Collection succeeds without a live server; marked smoke tests fail clearly when it is unavailable.
