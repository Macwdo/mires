---
name: macwdo-python-fastapi-celery-integration
description: Macwdo's FastAPI and Celery integration pattern for Python repos. Use for start and status routes, durable processing or job rows, commit-before-enqueue behavior, scalar Celery task payloads, route-visible delay calls, task status polling, and keeping FastAPI request state out of workers.
---

# FastAPI Celery Integration

Use this skill when an HTTP endpoint starts background work through Celery and the API needs to return a job or processing id.

## Source Repo Signals

- Routes create durable processing rows, commit, enqueue, and return processing ids: `src/api/routes/products/routes.py:24`, `src/api/routes/products/routes.py:30`, `src/api/routes/products/routes.py:32`, `src/api/routes/groups/routes.py:29`, `src/api/routes/groups/routes.py:35`, `src/api/routes/groups/routes.py:37`.
- Routes enqueue tasks lazily inside handlers to avoid import cycles during app startup: `src/api/routes/products/routes.py:18`, `src/api/routes/groups/routes.py:27`.
- Task payloads are scalar identifiers, not ORM objects or request objects: `src/tasks.py:18`, `src/tasks.py:27`, `src/api/routes/products/routes.py:32`, `src/api/routes/groups/routes.py:37`.
- Services update processing status after the worker starts and completes the work: `src/vendor/services/product.py:39`, `src/vendor/services/product.py:67`, `src/vendor/services/group.py:33`, `src/vendor/services/group.py:61`, `src/vendor/services/group.py:65`.

## Preferred Shape

Use this route shape when a FastAPI endpoint starts background work:

```python
@router.post("/process", response_model=ProcessStartResponse)
async def start_process(
    request: ProcessStartRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    processing = Processing(status=ProcessingStatus.PENDING)
    session.add(processing)
    await session.flush()
    await session.refresh(processing)
    await session.commit()

    process_thing_task.delay(processing_id=processing.id, thing_id=request.thing_id)
    return ProcessStartResponse(processing_id=processing.id, status=processing.status)
```

Use this worker shape for async service delegation:

```python
@shared_task
def process_thing_task(processing_id: int, thing_id: int) -> None:
    async def run() -> None:
        async with db.get_engine(postgres_uri=settings.POSTGRES_URI) as engine:
            await services.process_thing(
                processing_id=processing_id,
                thing_id=thing_id,
                engine=engine,
            )

    asyncio.run(run())
```

## Rules

- Keep route code responsible for validation, initial row creation, enqueueing, and response shaping.
- Commit before enqueue. A worker must never receive an id that is still inside an uncommitted HTTP transaction.
- Keep task payloads stable and serializable: ids, strings, numbers, booleans, and small dicts only.
- Use task status tables when the API needs polling. Model status with a shared enum such as `ProcessingStatus`: `src/db/models/base.py:8`.
- Let routes expose status reads separately from start endpoints. Source: `src/api/routes/products/routes.py:44`, `src/api/routes/groups/routes.py:41`.
- Keep worker services independent of FastAPI request state.
- Make workers receive ids and create their own resources.
- Keep the API contract simple: start endpoint returns processing id and initial status; status endpoint returns current status; result endpoint reads completed data if applicable.

## Anti-Patterns

- Do not enqueue before the processing row is committed.
- Do not pass ORM instances, sessions, clients, files, request objects, or large payloads to tasks.
- Do not make task code depend on FastAPI dependency injection.
- Do not bury `.delay(...)` calls in deep service code when the user-facing operation is an HTTP start endpoint; keep enqueue points visible at the route boundary.
