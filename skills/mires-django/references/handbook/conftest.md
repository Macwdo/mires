# Root pytest Fixtures

## Purpose and when to use it

This root fixture module supplies a stable password and API client helpers without creating tenant state implicitly.

## When not to use it

Feature-specific objects belong in their application test helpers.

## Complete canonical artifact

<!-- artifact: conftest.py; profiles: base -->
```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_password() -> str:
    return "correct-horse-battery-staple"
```

## Required tests

Collect the suite with `pytest --collect-only`.
