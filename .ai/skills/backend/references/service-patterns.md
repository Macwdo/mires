---
name: service-patterns
description: Mires's Python service-layer patterns. Use for async service functions, dependency injection of database sessions, engines and external clients, Celery task delegation, product import workflows, grouping workflows, file storage services, status transitions, and keeping business logic out of FastAPI routes.
---

# Python Service Patterns

Use this skill when implementing or reviewing service-layer code under `src/services` or `src/vendor/services`.

For Celery worker wrappers, also use `celery-app-setup`. For API route boundaries, also use `patterns`.

## Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing service, repository, dependency-injection, transaction, external-client, and error-handling boundaries override the examples below. Treat source repo signals as examples only when they match the target repository.

## Source Repo Signals

- Domain service functions are async and keyword-only: `src/vendor/services/product.py:22`, `src/vendor/services/group.py:20`, `src/services/file.py:15`.
- Services receive infrastructure dependencies explicitly: `src/vendor/services/product.py:27`, `src/vendor/services/product.py:28`, `src/vendor/services/product.py:29`, `src/vendor/services/product.py:30`, `src/services/file.py:18`, `src/services/file.py:19`.
- Long workflows own a transaction with `db.get_session(...), db_session.begin()`: `src/vendor/services/product.py:33`, `src/vendor/services/group.py:26`.
- Services update durable processing status during background work: `src/vendor/services/product.py:39`, `src/vendor/services/product.py:67`, `src/vendor/services/group.py:33`, `src/vendor/services/group.py:61`, `src/vendor/services/group.py:65`.
- Celery tasks are thin wrappers that create worker-local infrastructure and delegate to services: `src/tasks.py:17`, `src/tasks.py:20`, `src/tasks.py:21`, `src/tasks.py:26`, `src/tasks.py:33`, `src/tasks.py:37`, `src/tasks.py:38`.
- Shared infrastructure helpers live under `src/services`: S3/SQS settings helpers at `src/services/aws.py:8`, `src/services/aws.py:17`; file download at `src/services/file.py:15`.

## Service Shape

Prefer functions over classes unless there is real shared state:

```python
async def do_work(
    *,
    processing_id: int,
    engine: AsyncEngine,
    external_client: ExternalClient,
) -> Result:
    async with db.get_session(engine=engine) as session, session.begin():
        processing = await session.get(Processing, processing_id)
        if processing is None:
            logger.error("Processing not found for ID: %s", processing_id)
            return

        processing.status = ProcessingStatus.PROCESSING
        ...
        processing.status = ProcessingStatus.COMPLETED
        return result
```

For small route-owned operations, pass the request-scoped session and concrete collaborators explicitly. Keep optional domain fields before infrastructure dependencies and keep the signature keyword-only:

```python
async def create_product(
    *,
    sku: str,
    name: str,
    price: float,
    vendor_id: int,
    db_session: AsyncSession,
    embedding_client: EmbeddingClient,
    description: str | None = None,
    brand: str | None = None,
    category: str | None = None,
) -> Product:
    product = Product(
        sku=sku,
        name=name,
        price=price,
        vendor_id=vendor_id,
        description=description,
        brand=brand,
        category=category,
    )
    db_session.add(product)
    await db_session.flush()
    return product
```

For infrastructure-backed services, build clients at the route or task boundary and pass them in. The service may use settings for domain constants such as bucket names, but the network client remains injectable:

```python
async def download_file(
    *,
    file_id: int,
    s3_client: S3Client,
    db_session: AsyncSession,
) -> Path:
    file = await db_session.get(File, file_id)
    if file is None:
        raise FileNotFoundError(f"File with ID {file_id} not found")

    url = generate_get_presigned_url(
        bucket_name=settings.FILE_BUCKET_NAME,
        key=file.key,
        s3_client=s3_client,
    )
    return await stream_url_to_temp_file(url=url, suffix=f".{file.extension}")
```

## Boundary Rules

- Routes should orchestrate HTTP concerns and delegate business logic.
- Tasks should build worker-local infrastructure and delegate business logic.
- Services should accept ids, sessions or engines, and explicit clients.
- Do not read FastAPI `Request` or app state in service code.
- Do not create global SDK clients for code that needs test fakes.
- Keep private helpers next to the service that owns them.
- Use logging for operational context, but avoid swallowing exceptions that should mark a job failed.

## Database Rules

- Pass an `AsyncSession` for small operations that are part of a route transaction.
- Pass an `AsyncEngine` when the service owns the whole background transaction.
- Use `flush()` and `refresh()` after adding rows whose ids are needed.
- Use `selectinload(...)` in query services that feed nested API responses.
- Keep status transitions consistent for background processing: `pending` in the route, `processing` at worker start, `completed` or `failed` in the service.

## External Client Rules

- Build S3, LLM, embedding, and broker clients at the route/task boundary or dependency layer.
- Pass those clients into services.
- Keep helper functions such as `get_s3_client_kwargs()` settings-only and side-effect-light.
- For tests, fake external clients at the service boundary.

## Failure Rules

- Background services should persist `FAILED` before re-raising or returning from known failure paths.
- Do not rely on Celery result backend state as the source of truth for application workflows.
- Prefer explicit domain exceptions when callers need to translate service failures into HTTP errors.

## Checklist

- Function has keyword-only parameters and explicit dependencies.
- Business logic is outside the route and outside the Celery task wrapper.
- Database transaction scope is clear.
- External clients are injectable and easy to fake.
- Background status transitions cover success and failure.
- Tests can call the service directly without a running API or worker.
