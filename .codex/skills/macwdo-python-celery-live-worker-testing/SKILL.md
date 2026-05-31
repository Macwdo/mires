---
name: macwdo-python-celery-live-worker-testing
description: Macwdo's live Celery worker testing pattern for Python and FastAPI workflows. Use when testing actual task execution through delay or apply_async, task registration, serialization, queue routing, worker imports, retries, and database status transitions caused by a real worker and broker.
---

# Celery Live Worker Testing

Use this skill for integration tests that must prove the real Celery execution path works:

```text
FastAPI route or service -> task.delay/apply_async -> broker -> worker -> task -> service -> database update
```

This is not the default test layer. Keep these tests few, focused, and marked as integration.

## When to Use

Use live worker tests when you need to verify:

- A task is registered correctly.
- `.delay()` or `.apply_async()` reaches the broker.
- Task payloads serialize and deserialize correctly.
- The worker can import and execute the task.
- Queue or routing configuration is honored.
- Retries work with a real worker.
- Task failure persists the expected application state.
- The full API-to-worker-to-database flow works.

Prefer faster service, route enqueue, and task wrapper tests for business rules, validation, response schemas, external API fakes, and ordinary status transitions.

## Test Strategy

Use three layers:

1. Service tests
   - Call async services directly.
   - Use a test database session and fake external clients.
   - Assert business behavior and status transitions.

2. Route enqueue tests
   - Use FastAPI dependency overrides.
   - Monkeypatch `task.delay` or `task.apply_async`.
   - Assert the route creates the processing/job row before enqueueing.
   - Do not start a real Celery worker.

3. Live worker integration tests
   - Use a real broker and a real Celery worker.
   - Send the task through `.delay()` or `.apply_async()`.
   - Poll the database until the worker updates the processing/job row.
   - Mark tests with `@pytest.mark.integration`.

Default split: 80-90% service, route, and task wrapper tests; 10-20% live worker integration tests; very few Docker-based smoke tests.

## Pytest Setup

Install Celery pytest support:

```bash
pip install "celery[pytest]"
```

Enable the plugin:

```python
pytest_plugins = ("celery.contrib.pytest",)
```

Configure pytest:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
markers = [
    "integration: tests that require external services like Redis, RabbitMQ, Postgres, or Celery workers",
]
```

Run fast tests with `pytest -m "not integration"` and live worker tests with `pytest -m integration`.

## Celery Test Configuration

Use a dedicated test broker namespace. Never use production broker URLs in tests.

```python
import pytest

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "redis://localhost:6379/15",
        "result_backend": "redis://localhost:6379/15",
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "task_track_started": True,
    }


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"shutdown_timeout": 10}
```

## Minimal Worker Check

```python
def test_celery_worker_executes_task(celery_app, celery_worker):
    @celery_app.task
    def add(x: int, y: int) -> int:
        return x + y

    celery_worker.reload()

    result = add.delay(2, 3)

    assert result.get(timeout=10) == 5
```

This proves the test can publish to the broker, the worker can consume the task, and the result backend is reachable.

## FastAPI Flow Pattern

```python
import asyncio
import pytest

from src.models import Processing, ProcessingStatus


@pytest.mark.integration
async def test_route_creates_processing_and_worker_completes_it(
    async_client,
    db_session,
    celery_worker,
):
    response = await async_client.post("/things/process", json={"thing_id": 123})

    assert response.status_code == 200

    processing_id = response.json()["processing_id"]

    processing = await wait_for_processing_status(
        db_session=db_session,
        model=Processing,
        processing_id=processing_id,
        expected_status=ProcessingStatus.COMPLETED,
    )

    assert processing.completed_at is not None
    assert processing.error_message is None
```

Add a failure-path test for each Celery-backed workflow where failure state is part of the application contract:

```python
@pytest.mark.integration
async def test_worker_marks_processing_failed_when_task_fails(
    async_client,
    db_session,
    celery_worker,
    monkeypatch,
):
    async def fake_process(*args, **kwargs):
        raise RuntimeError("external service failed")

    monkeypatch.setattr("src.my_domain.services.process_thing", fake_process)

    response = await async_client.post("/things/process", json={"thing_id": 123})

    assert response.status_code == 200

    processing = await wait_for_processing_status(
        db_session=db_session,
        model=Processing,
        processing_id=response.json()["processing_id"],
        expected_status=ProcessingStatus.FAILED,
    )

    assert processing.error_message is not None
```

## Polling Helper

Poll application state instead of using fixed sleeps.

```python
import asyncio


async def wait_for_processing_status(
    *,
    db_session,
    model,
    processing_id: int,
    expected_status,
    timeout_seconds: float = 10,
    interval_seconds: float = 0.5,
):
    attempts = int(timeout_seconds / interval_seconds)

    for _ in range(attempts):
        processing = await db_session.get(model, processing_id)

        if processing.status == expected_status:
            return processing

        await asyncio.sleep(interval_seconds)

    processing = await db_session.get(model, processing_id)

    raise AssertionError(
        f"Expected processing {processing_id} to become "
        f"{expected_status}, got {processing.status}"
    )
```

## Task Design for Testability

Prefer tasks that receive primitive ids, build worker-local dependencies, and delegate business behavior to a service:

```python
@celery_app.task(name="process_thing")
def process_thing_task(*, processing_id: int, thing_id: int) -> None:
    run_async(
        process_thing_service(
            processing_id=processing_id,
            thing_id=thing_id,
            engine=create_engine(),
            client=create_external_client(),
        )
    )
```

Assert application outcomes, not private Celery internals:

```python
assert processing.status == ProcessingStatus.COMPLETED
assert processing.completed_at is not None
assert processing.error_message is None
```

## Docker Smoke Tests

Use `pytest-celery` only for production-like smoke tests that need Docker-based infrastructure, such as worker container startup, app-to-broker publishing, expected queue consumption, and production Celery config loading. Keep these tests very few.

## Rules

- Mark live worker tests with `@pytest.mark.integration`.
- Do not run live worker tests in the default fast test suite.
- Use a test broker, never production broker URLs.
- Use primitive ids in task payloads.
- Assert database state transitions.
- Prefer polling the database instead of sleeping for a fixed time.
- Keep business logic assertions in service tests.
- Keep task tests focused on the worker path.
- Add at least one success-path live worker test.
- Add at least one failure-path live worker test when failure state is part of the contract.
- Add retry tests only when retries are part of the application contract.

## Anti-Patterns

- Do not make every test require Redis, RabbitMQ, or a Celery worker.
- Do not test all business rules through Celery.
- Do not pass ORM objects to tasks.
- Do not use production `.env` values.
- Do not rely on `task_always_eager` when the goal is to prove real worker behavior.
- Do not assert private Celery internals.
- Do not use fixed long sleeps when polling is possible.
- Do not hide worker errors by only asserting the HTTP response.
- Do not use the result backend as the source of truth unless the application uses it directly.
