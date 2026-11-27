# pytest Configuration

## Purpose and when to use it

Use pytest-django for deterministic unit and integration tests.

## Complete canonical artifact

<!-- artifact: pytest.ini; profiles: base -->
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
pythonpath = src
python_files = test_*.py
addopts = -ra --strict-config --strict-markers
markers =
    integration: requires external infrastructure
    realtime: exercises ASGI or WebSocket behavior
```

## Responsibilities and invariants

Unknown configuration and markers fail collection. External-service tests opt into explicit markers.

## Required tests

Run the complete suite and collect tests in isolation.
