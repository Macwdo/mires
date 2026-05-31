---
name: macwdo-python-celery-testing
description: Macwdo's fast Celery testing pattern for Python and FastAPI workflows. Use for service tests, route enqueue tests, task wrapper tests, eager mode decisions, broker-free unit tests, job status transitions, failure status assertions, and pytest async configuration. For real worker and broker tests, use macwdo-python-celery-live-worker-testing.
---

# Celery Testing

Use this skill when writing fast tests for services, FastAPI routes, Celery task wrappers, or broker-free background job behavior.

For tests that must prove `.delay()` or `.apply_async()` reaches a real broker and worker, use `macwdo-python-celery-live-worker-testing` instead.

## Source Repo Signals

- Test tooling is configured in `pyproject.toml`: pytest, pytest-asyncio, pytest addopts, and `asyncio_mode = "auto"`: `pyproject.toml:28`, `pyproject.toml:33`, `pyproject.toml:35`, `pyproject.toml:88`.
- No `tests/` directory or `test_*.py` files are present. Treat these rules as the standard to add, not as a description of existing tests.

## Test Layers

1. Service tests
   - Call async service functions directly.
   - Pass a test `AsyncSession` or test engine and fake external clients.
   - Assert domain side effects and processing status transitions.
   - Prefer this layer for business behavior.

2. Route tests
   - Use FastAPI dependency overrides for database sessions and external clients.
   - Monkeypatch `task.delay` and assert it is called after the processing row exists.
   - Assert the response schema contains the processing id and initial status.
   - Do not start a real Celery worker for ordinary route tests.

3. Task wrapper tests
   - Test that the task builds required clients and delegates to the service with ids.
   - Use Celery eager mode or call the task function directly.
   - Monkeypatch engine and client factories to avoid network calls.

4. Narrow integration tests without a live worker
   - Use Docker Compose or testcontainers-style infrastructure when the database or broker-adjacent configuration must exist.
   - Keep assertions on application state and wiring, not Celery internals.
   - If the worker must consume from the broker, switch to `macwdo-python-celery-live-worker-testing`.

## Minimal Examples

```python
async def test_service_marks_processing_completed(db_session, fake_client):
    processing = Processing(status=ProcessingStatus.PENDING)
    db_session.add(processing)
    await db_session.commit()

    await service.process(processing_id=processing.id, db_session=db_session, client=fake_client)

    await db_session.refresh(processing)
    assert processing.status == ProcessingStatus.COMPLETED
```

```python
async def test_route_commits_then_enqueues(async_client, monkeypatch):
    calls = []

    def fake_delay(*, processing_id: int, thing_id: int) -> None:
        calls.append((processing_id, thing_id))

    monkeypatch.setattr("src.tasks.process_thing_task.delay", fake_delay)

    response = await async_client.post("/things/process", json={"thing_id": 123})

    assert response.status_code == 200
    assert response.json()["processing_id"]
    assert calls == [(response.json()["processing_id"], 123)]
```

```python
def test_task_delegates_to_service(monkeypatch):
    seen = {}

    async def fake_process(*, processing_id: int, thing_id: int, engine):
        seen["args"] = (processing_id, thing_id)

    monkeypatch.setattr("src.my_domain.services.process_thing", fake_process)

    process_thing_task(processing_id=1, thing_id=2)

    assert seen["args"] == (1, 2)
```

## Rules

- Configure pytest with async mode enabled for async FastAPI and SQLAlchemy code.
- Test status transitions, not only task enqueue calls.
- Use fakes for external APIs and clients by default.
- Keep task tests focused on wiring. Put behavior assertions in service tests.
- Add at least one failure-path test that proves status becomes `FAILED` when a service raises after processing starts.
- Add migration smoke tests when task tables or status enums change.
- Keep real broker and worker checks in a small `@pytest.mark.integration` live-worker suite.

## Anti-Patterns

- Do not make every test require a live broker.
- Do not assert Celery internals when the contract is route enqueues task with ids.
- Do not test async services only through Celery; it slows feedback and hides service errors.
- Do not use production `.env` values in tests.
- Do not rely on task result backend state unless the application explicitly uses a result backend.
- Do not rely on `task_always_eager` when the goal is to prove real worker behavior.
