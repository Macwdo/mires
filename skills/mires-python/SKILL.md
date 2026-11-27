---
name: mires-python
description: Apply Macwdo's idiomatic Python and backend standards for functions, typing, modules, services, configuration, SQLAlchemy, Postgres, Celery, and tests. Use for Python work outside Django and LangChain-specific agent workflows; FastAPI routes use $mires-fastapi.
---

# Mires Python

Use one coherent Python style across plain modules and backend infrastructure. Inspect the repository first; its established conventions override the examples in this skill.

## Snippet-Driven Implementation

Always use the closest Python snippet in this `SKILL.md` as the starting reference for generated code. Match its function-first design, annotations, keyword-only service boundaries, explicit dependencies, narrow errors, and testable return values.

Before writing code:

1. Find the snippet for the touched boundary: plain function, service, settings, SQLAlchemy, Postgres, Alembic, Celery, or test.
2. Compare it with sibling modules and tests in the target repository.
3. Adapt names, imports, sync/async style, settings, sessions, and exceptions to the existing project.
4. Keep the reference snippet's structural invariants unless local evidence requires otherwise.
5. Do not introduce a dependency or abstraction shown in a snippet when the repository uses a different established equivalent.

Generated Python must be recognizably derived from the nearest snippet while remaining native to the repository.

## Scope And Companion Routing

- This skill owns idiomatic Python, functions, annotations, module design, errors, validation, testing, services, settings, SQLAlchemy, Postgres, migrations, Celery, and local infrastructure.
- Use `$mires-fastapi` when FastAPI owns the HTTP boundary.
- Use `$mires-python-django` when Django or DRF owns the application boundary.
- Use `$mires-python-langchain` for LangChain, LangGraph, Deep Agents, document loaders, retrieval, or agent workflows.
- Use `$mires-typescript` when a Python API contract changes a TypeScript consumer.

## Implementation Gate

Before editing backend code, report the repository's configuration pattern, database and session pattern, dependency-injection style, service and repository boundaries, error handling, testing style, naming, and module organization. Existing evidence wins over generic examples.

## Expected Python Quality

Python should be explicit without being ceremonial: typed public boundaries, small cohesive functions, visible dependencies, predictable errors, narrow mutation, and tests that describe behavior. Prefer standard language features and the repository's existing abstractions over framework-shaped indirection.

## Required Python Toolchain: uv, Ruff, And ty

Use one Astral-based toolchain for Python projects unless the repository has an explicit migration constraint:

- `uv` owns Python versions, virtual environments, dependencies, lockfiles, scripts, and tool execution.
- Ruff owns formatting, import sorting, and linting.
- `ty` owns static type checking.
- pytest owns behavior tests.

Do not add Poetry, Pipenv, a hand-built `venv`, Black, isort, Flake8, mypy, or Pyright alongside this baseline. Migrate intentionally if an existing repository uses them; do not run two formatters or type checkers indefinitely.

### Bootstrap And Dependency Commands

```bash
uv init
uv python pin 3.12
uv add httpx pydantic
uv add --dev pytest ruff ty
uv sync
```

- Use `uv add` and `uv remove` instead of editing dependency arrays by hand.
- Commit `pyproject.toml`, `.python-version`, and `uv.lock` when the repository tracks them.
- Run project commands through `uv run`; use `uvx` only for an intentionally ephemeral tool.
- Put local-only tools in `[dependency-groups].dev`, not published runtime dependencies.

### pyproject.toml Reference

```toml
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pytest",
  "ruff",
  "ty",
]

[tool.ruff]
target-version = "py312"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

[tool.ty.src]
include = ["src", "tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Let `project.requires-python` define the minimum Python version for both code and `ty`. Configure `[tool.ty.environment]` only when the repository uses a nonstandard source root, interpreter, platform, or Python target.

### Typing Rules

- Type every public function and method: parameters, return value, yielded value, callback, and important attributes.
- Use `collections.abc` for callable and collection protocols and built-in generics such as `list[str]` and `dict[str, object]`.
- Use `Protocol` for injected behavior, Pydantic models for DTOs, `TypedDict` for dictionary contracts that remain dictionaries, and dataclasses for value objects.
- Keep `Any` at an untyped external boundary; validate or narrow it immediately instead of allowing it into domain code.
- Prefer `object` for an unknown value that must be narrowed and a type variable for values that must preserve their type.
- Use `Self` for fluent methods and `TypeVar` only when a real relationship between input and output types exists.
- Use `cast()` only after a runtime invariant is already established; a cast is not validation.
- Use `# ty: ignore[rule-name]` only on the smallest affected line with a concrete reason. Never add blanket ignores to make the check green.
- Do not configure mypy plugins for `ty`; `ty` does not execute them.

### Typed Boundary Reference

```python
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


class PriceSource(Protocol):
    def price_for(self, item_id: str) -> int: ...


@dataclass(frozen=True, slots=True)
class PricedItem:
    item_id: str
    price_cents: int


def price_items(
    item_ids: Iterable[str],
    *,
    source: PriceSource,
) -> list[PricedItem]:
    return [
        PricedItem(item_id=item_id, price_cents=source.price_for(item_id))
        for item_id in item_ids
    ]
```

### Required Validation Order

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
```

Run `uv run ruff format .` and `uv run ruff check . --fix` while implementing, then use the check-only commands before handoff. A Python change is not fully validated when formatting, linting, typing, or relevant tests were skipped without an explicit reason.

## Python

Generic Python module, typing, boundary, error, and test guidance for backend code.

### When To Use

Use for generic Python implementation decisions that are not framework-specific.

### Core Rules

- Prefer small typed functions unless the repo clearly favors another shape.
- Keep I/O boundaries explicit.
- Match nearby naming, imports, and helper placement.
- Reuse the existing testing and validation workflow.

### Preferred Patterns

- Explicit function signatures.
- Visible dependency injection.
- Focused modules with clear ownership.
- Behavior-first tests.

### Anti-Patterns

- Hidden global state.
- Implicit side effects.
- Oversized modules with mixed concerns.
- Unchecked assumptions about typing or mutation.

### Checklist

- Confirm the existing module shape.
- Confirm the current typing and validation style.
- Reuse existing test helpers and workflows.
- Keep changes local to the touched behavior.

---

### Python Functions

Use this section when deciding whether Python code should be a function, class, service helper, or utility module.

#### Rules

- Read the target file, sibling modules, and nearby tests before introducing a new shape.
- Prefer plain functions for services, transformations, orchestration helpers, command helpers, and utilities.
- Introduce a class only when the code needs durable state, a protocol boundary, or a cohesive object lifecycle.
- Keep framework glue thin and keep plain Python in the middle of the implementation.
- Keep public entry points easy to grep and helpers close to the code that uses them.

#### Workflow

1. Match the repo naming and import style.
2. Write the smallest useful public function first.
3. Extract helpers only after the main responsibility is obvious.

---

### Python Typing Signatures

Use this section when adding or refactoring typed Python APIs.

#### Rules

- Add type hints to public functions, methods, return values, and important local data structures.
- Prefer concrete types such as `list[str]`, `Path`, and domain-specific aliases over vague placeholders. Do not annotate dictionaries with an unconstrained value type.
- Use keyword-only arguments for service-style functions, helpers, and orchestration entry points when clarity improves.
- Use `TypedDict` when a value stays a dictionary and its keys are known. Use a Pydantic model for DTOs.
- Keep types aligned with the repo type checker and Python version.

#### Example

```python
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class ReportSummary(BaseModel):
    path: Path
    line_count: int


def summarize_report(*, path: Path) -> ReportSummary:
    line_count = len(path.read_text().splitlines())
    return ReportSummary(path=path, line_count=line_count)
```

---

### Python Boundaries Dependencies

Use this section when code touches external services, repositories, clients, framework adapters, or environment configuration.

#### Rules

- Pass external clients, repositories, and configurable collaborators into functions instead of constructing them deep inside business logic.
- Keep I/O, network calls, filesystem access, framework adapters, and environment reads at module boundaries.
- Keep core logic testable without booting a framework or patching module globals.
- Use dependency functions at the edge when callers need SDK clients or app settings.
- Prefer explicit collaborators over implicit singletons.

#### Example

```python
from collections.abc import Callable


def build_invoice_message(
    *,
    customer_name: str,
    total_cents: int,
    format_currency: Callable[[int], str],
) -> str:
    return f"{customer_name}: {format_currency(total_cents)}"
```

At framework edges, keep SDK construction separate from business logic. Settings-only helpers are easy to test and can be reused by FastAPI dependencies, Celery app setup, and task wrappers:

```python
import boto3


def get_s3_client_kwargs(*, settings: Settings) -> dict[str, str]:
    return {
        "aws_access_key_id": settings.storage_access_key,
        "aws_secret_access_key": settings.storage_secret_key,
        "region_name": settings.storage_region,
        "endpoint_url": settings.storage_endpoint_url,
    }


def get_s3_client(*, settings: Settings):
    return boto3.client("s3", **get_s3_client_kwargs(settings=settings))
```

For direct browser uploads, keep the boto3 response behind a typed adapter. Sign the server-generated object key and bind the POST policy to the content type and expected size recorded by the application:

```python
from typing import TypedDict

from mypy_boto3_s3 import S3Client


class PresignedPost(TypedDict):
    url: str
    fields: dict[str, str]


def generate_upload_presigned_post(
    *,
    bucket_name: str,
    object_key: str,
    content_type: str,
    expected_size: int,
    expires_in: int,
    s3_client: S3Client,
) -> PresignedPost:
    response = s3_client.generate_presigned_post(
        Bucket=bucket_name,
        Key=object_key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", expected_size, expected_size],
        ],
        ExpiresIn=expires_in,
    )
    fields = {str(key): str(value) for key, value in response["fields"].items()}
    return PresignedPost(url=str(response["url"]), fields=fields)
```

The application can expose a separate confirmation endpoint after the browser finishes the signed POST. Apply `$mires-python-django` for the connected Django and DRF start/confirm workflow.

Apply the same boundary to HTTP clients. Return a configured client from an adapter function, then pass it into the service or manage it with `async with` at the call site:

```python
import httpx


def http_client_kwargs() -> dict[str, float]:
    return {"timeout": 10.0}


def get_async_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(**http_client_kwargs())
```

---

### Python Module Shape

Use this section when creating a module, splitting a file, or cleaning up Python organization.

#### Rules

- Start with the smallest useful module.
- Keep public entry points near the top and helpers below them.
- Extract a new file when a module mixes unrelated responsibilities or becomes hard to scan.
- Reuse the repo package layout, import grouping, naming, and error model when those conventions already exist.
- Add short docstrings where they clarify a public API or a non-obvious rule.

---

### Python State Mutation

Use this section when refactoring functions that update state, shared objects, caches, or mutable inputs.

#### Rules

- Prefer returning new values over mutating shared state in place.
- If a function updates state, make the side effect explicit in the function name and signature.
- Avoid hidden global caches, mutable singletons, and mutable default arguments in normal application code.
- Keep transaction-like state changes close to their boundary so tests can assert observable effects.
- Document only non-obvious side effects; do not comment obvious assignments.

---

### Python Errors

Use this section when adding or reviewing exception behavior in Python modules and services.

#### Rules

- Raise explicit exceptions with human-readable messages.
- Do not swallow exceptions just to keep control flow moving.
- Translate low-level exceptions at boundaries when the caller needs a more useful domain error.
- Keep retry, logging, and fallback behavior tied to a real operational need.
- Test raised exceptions and failure-side effects when they are part of the caller-visible contract.

---

### DevEx Patterns

Use this section when changing project tooling, local commands, README setup instructions, or test/lint configuration.

#### Command Rules

- Prefer `uv sync` for dependency installation.
- Prefer `uv run <command>` when running Python tools in the project environment.
- Use `uv run ruff format`, `uv run ruff check`, and `uv run ty check` as the standard quality gates.
- Keep repeatable local workflows in `Makefile`.
- Keep Makefile target names short and action-oriented.
- Update README commands when Makefile or startup commands change.

#### Dependency Rules

- Add runtime packages under `[project].dependencies`.
- Add local tooling under `[dependency-groups].dev`.
- After dependency changes, expect `uv.lock` to change.
- Do not manually edit `uv.lock`; update it through `uv`.

#### Lint and Format Rules

- Use Ruff as the formatter and linter.
- Respect the existing line length and quote style.
- Keep Alembic migrations excluded from Ruff unless the migration style is intentionally changed.
- Prefer fixing lint issues in touched code only unless the user asks for a cleanup pass.
- Keep pre-commit hooks aligned with pyproject tooling.

Minimal `pyproject.toml` shape for a new Python service:

```toml
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pre-commit",
  "ruff",
  "ty",
]

[tool.ruff]
target-version = "py312"
exclude = ["__pycache__", ".git", ".venv", "build", "dist", "alembic/**"]
include = ["**/*.py", "**/*.pyi"]
line-length = 120
fix = true
preview = true

[tool.ruff.lint]
select = [
  "E",
  "F",
  "I",
  "UP",
  "B",
  "ARG",
  "TID",
  "RUF",
  "SIM",
  "C4",
  "ERA",
  "PIE",
  "PERF",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
docstring-code-format = true
docstring-code-line-length = "dynamic"

[tool.ty.src]
include = ["src", "tests"]
```

#### Test Rules

- Use pytest for tests.
- Async tests should rely on `asyncio_mode = "auto"`.
- Add markers to `[tool.pytest.ini_options]` when introducing integration tests.
- Keep default test runs fast. Mark external-service tests separately.

#### Local Infra Rules

- Use `make up` to start local infrastructure and apply migrations.
- Keep queue or bucket provisioning idempotent.
- Use `make down` for teardown.
- Avoid adding local-only setup steps that are not represented in Makefile or README.

#### Checklist

- `pyproject.toml`, `uv.lock`, pre-commit, and README agree.
- New commands use `uv run` where appropriate.
- Ruff formatting, Ruff linting, and `ty` checking pass.
- Makefile remains the primary local workflow.
- Tests remain fast by default.
- Integration-test markers are configured when needed.
- Tooling changes do not modify application behavior accidentally.

---

### Python Tests Helpers

Use this section when test setup repeats or needs fixtures, helpers, or mocks.

#### Rules

- Prefer small helpers and explicit fixtures over hidden setup chains.
- Keep data construction close to the test unless it is genuinely repeated.
- Mock only the true external boundary, not the logic under test.
- Use keyword-only arguments in reusable helpers when setup needs variation.
- Keep monkeypatching and patching near the test that needs it.

---

### Python Tests Workflow

Use this section when adding or changing Python tests outside a framework-specific flow.

#### Rules

- Inspect the current test suite before adding new tests.
- Default to `pytest` when the repo has no stronger convention.
- Write tests around user-visible or caller-visible contracts first.
- Assert return values, raised exceptions, and observable side effects.
- Name tests so the condition and expected outcome are obvious.

#### Workflow

1. Start from the behavior.
2. Make the smallest production change that satisfies it.
3. Run the narrowest command that proves the behavior.

---

### Python Validation

Use this section before finishing Python implementation work.

#### Rules

- Run the smallest validation that proves the change works.
- Prefer a focused `pytest` target, a single module test run, or the narrowest lint/type check that covers the edit.
- Run Ruff formatting and linting, then `uv run ty check`, then the relevant pytest scope.
- Treat typing as a default Python quality gate, not an optional check only for typing-heavy changes.
- If formatting matters, run the repo formatter instead of hand-formatting around it.
- Do not claim confidence without running at least one relevant check when a check is available.

## Backend

Backend architecture and service-layer rules for Python applications after local conventions are inspected.

### When To Use

Use for backend architecture, service-layer boundaries, settings usage, Docker Compose setup, and backend integration decisions that are broader than one framework.

### Core Rules

- Inspect repository conventions before proposing abstractions.
- Keep business logic out of framework entrypoints.
- Reuse the existing settings, dependency, and service boundaries.
- Prefer small reversible changes when the local pattern is unclear.

### Preferred Patterns

- Thin routes, views, handlers, and tasks.
- Explicit service or orchestration layers.
- Settings-driven construction.
- Focused validation matched to the touched boundary.

### Anti-Patterns

- Inventing a new backend architecture without local evidence.
- Mixing business logic into controllers, routes, or tasks.
- Adding duplicate settings, client factories, or session management layers.

### Checklist

- Inspect project conventions first.
- Identify the existing service and dependency boundaries.
- Pick only the backend-adjacent references that match the repo.
- Validate the touched backend path.

---

### Python Service Patterns

Use this section when implementing or reviewing service-layer code in the repository's established service modules.

For Celery worker wrappers, apply the Celery App Setup section later in this `SKILL.md`. For FastAPI route boundaries, apply `$mires-fastapi`.

#### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing service, repository, dependency-injection, transaction, external-client, and error-handling boundaries override the examples below.

#### Service Shape

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
async def create_item(
    *,
    external_id: str,
    name: str,
    price: float,
    owner_id: int,
    db_session: AsyncSession,
    description: str | None = None,
) -> Item:
    item = Item(
        external_id=external_id,
        name=name,
        price=price,
        owner_id=owner_id,
        description=description,
    )
    db_session.add(item)
    await db_session.flush()
    return item
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

#### Boundary Rules

- Routes should orchestrate HTTP concerns and delegate business logic.
- Tasks should build worker-local infrastructure and delegate business logic.
- Services should accept ids, sessions or engines, and explicit clients.
- Do not read FastAPI `Request` or app state in service code.
- Do not create global SDK clients for code that needs test fakes.
- Keep private helpers next to the service that owns them.
- Use logging for operational context, but avoid swallowing exceptions that should mark a job failed.

#### Database Rules

- Pass an `AsyncSession` for small operations that are part of a route transaction.
- Pass an `AsyncEngine` when the service owns the whole background transaction.
- Use `flush()` and `refresh()` after adding rows whose ids are needed.
- Use `selectinload(...)` in query services that feed nested API responses.
- Keep status transitions consistent for background processing: `pending` in the route, `processing` at worker start, `completed` or `failed` in the service.

#### External Client Rules

- Build S3, LLM, embedding, and broker clients at the route/task boundary or dependency layer.
- Pass those clients into services.
- Keep helper functions such as `get_s3_client_kwargs()` settings-only and side-effect-light.
- For tests, fake external clients at the service boundary.

#### Failure Rules

- Background services should persist `FAILED` before re-raising or returning from known failure paths.
- Do not rely on Celery result backend state as the source of truth for application workflows.
- Prefer explicit domain exceptions when callers need to translate service failures into HTTP errors.

#### Checklist

- Function has keyword-only parameters and explicit dependencies.
- Business logic is outside the route and outside the Celery task wrapper.
- Database transaction scope is clear.
- External clients are injectable and easy to fake.
- Background status transitions cover success and failure.
- Tests can call the service directly without a running API or worker.

---

### Python Settings

Use this section when backend work touches application settings or environment configuration.

#### Discovery First

Before editing settings, inspect:

- Existing settings modules and imports.
- Framework settings such as Django settings or FastAPI app configuration.
- Dependencies in `pyproject.toml`, lockfiles, or requirements files.
- Environment examples such as `.env.example`, compose files, deployment docs, or README setup steps.
- Tests that override settings or environment values.

#### Rules

- Extend the repository's existing settings pattern instead of creating a parallel one.
- Use Pydantic Settings when the project already uses Pydantic Settings.
- Use Dynaconf when the project already uses Dynaconf.
- Use Django settings when the project is a Django project and settings are already centralized there.
- Use existing environment-only helpers when that is the established pattern.
- Do not introduce dataclass-based application settings when Pydantic Settings, Dynaconf, Django settings, or another established settings system exists.
- Do not read environment variables deep inside business logic when the project has a settings boundary.
- Keep settings construction at application, framework, CLI, worker, or dependency boundaries.
- Add new fields to the existing settings object, module, or framework settings surface.
- Keep secret examples as placeholders such as `OPENAI_API_KEY`; do not commit real secrets.

#### Review Checklist

- The chosen settings pattern is supported by local evidence.
- New settings live beside existing settings.
- Callers receive settings through the existing dependency, import, or framework pattern.
- Tests or docs are updated when new required environment values are introduced.
- No duplicate configuration object, dataclass config, or ad hoc environment reader was added.

---

### Docker Compose Patterns

Use this section when changing local Compose services or the Makefile workflow around local infrastructure.

For deeper local infrastructure examples, continue to Docker Compose Local Infra later in this document.

#### Compose Rules

- Keep local-only infrastructure in the repository's existing Compose file.
- Prefer explicit service names: `db`, `aws`, `minio`, and one-shot provisioning service names.
- Use `depends_on` with `condition: service_healthy` for services that truly require readiness.
- Add healthchecks for services that other services depend on.
- Use named volumes for stateful services.
- Keep ports explicit and predictable for local tools.
- Use `.env` interpolation for application-specific values such as bucket and queue names.
- Do not bake real credentials into Compose. Local demo credentials are acceptable only for local-only services.

#### One-Shot Provisioning Rules

- Use one-shot services for idempotent setup like bucket creation.
- Set `restart: "no"` on one-shot services.
- Make setup commands idempotent with `|| true` only where deleting/recreating local resources is intentional.
- Keep more complex provisioning in a small script when health polling or SDK calls are easier than shell.

#### Makefile Rules

- Keep `make up` as the end-to-end local bootstrap: Compose up, queue/bootstrap scripts, migrations.
- Keep `make down` as the matching teardown.
- Keep Alembic commands in Makefile targets so users do not need to remember raw CLI flags.
- Use `uv run` for Python scripts that depend on the project environment.

#### Adding API or Worker Services

When local end-to-end execution should be one command, add API and worker services to Compose:

- API command: `uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000`.
- Worker command: `uv run celery -A src.celery_app.app worker --loglevel=INFO`.
- Both should read `.env`.
- Both should depend on database and broker readiness.
- The worker should not expose ports unless needed for diagnostics.

#### Checklist

- New service has a clear local purpose.
- Stateful service has a named volume.
- Dependent services wait for health, not just container start.
- Makefile remains the primary local workflow.
- LocalStack and MinIO setup stays idempotent.
- No production credentials or URLs are introduced.

---

### Docker Compose Local Infra

Use this section when composing local API, worker, Postgres, Redis, SQS or LocalStack, MinIO, or local bootstrap services.

#### Preferred Compose Shape

For a FastAPI plus Celery repo, prefer one local Compose file with explicit API, worker, database, and broker services:

```yaml
services:
  api:
    build: .
    command: uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      broker:
        condition: service_healthy
    ports:
      - "8000:8000"

  worker:
    build: .
    command: uv run celery -A src.celery_app.app worker --loglevel=INFO
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      broker:
        condition: service_healthy

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  broker:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
```

For SQS or LocalStack instead of Redis, keep the broker in its own explicit service boundary:

```yaml
services:
  aws:
    image: localstack/localstack
    environment:
      - SERVICES=sqs
      - DEBUG=1
    ports:
      - "4566:4566"
```

Add a one-shot provisioning script or service that waits for LocalStack health and creates queues before workers start.

For S3-compatible local storage, pair the service with a one-shot bucket provisioner. Keep the bucket name in `.env`, wait for MinIO health, and make destructive reset behavior explicit:

```yaml
services:
  minio:
    image: minio/minio
    command: server /data --address 0.0.0.0:9000 --console-address :9001
    environment:
      MINIO_ROOT_USER: miniouser
      MINIO_ROOT_PASSWORD: miniopassword
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  createbucket:
    image: minio/mc
    depends_on:
      minio:
        condition: service_healthy
    environment:
      MINIO_AWS_BUCKET_NAME: ${MINIO_AWS_BUCKET_NAME}
    entrypoint: >
      sh -c "
        mc config host add --quiet --api s3v4 minio http://minio:9000 miniouser miniopassword;
        mc mb --quiet minio/$${MINIO_AWS_BUCKET_NAME} || true;
      "
    restart: "no"

volumes:
  minio_data:
```

#### Rules

- Give persistent infrastructure healthchecks and make dependent services wait on health.
- Use a pgvector-enabled Postgres image when the app stores pgvector embeddings.
- Keep local service names stable: `db`, `api`, `worker`, `broker`, and optional `aws` or `minio`.
- Use `.env` for local settings, but avoid committing secrets.
- Make `make up` idempotent enough to recreate local infra, provision broker queues or buckets, and apply migrations.
- Keep broker provisioning separate from application startup so API and worker commands stay simple.
- Include API and worker services once local end-to-end runs or integration tests depend on them.

#### Anti-Patterns

- Do not leave worker startup only in README once integration tests or full local runs depend on it.
- Do not hardcode SQS queue URLs that depend on generated LocalStack output; derive them from settings or provisioning output.
- Do not reset buckets or queues destructively unless local data loss is intended and clearly scoped.
- Do not copy SQS-specific `broker_transport_options` into Redis projects.
- Do not start migrations before Postgres is healthy.

## FastAPI

FastAPI app setup, routes, dependencies, schemas, session wiring, and Celery-backed endpoints live in `$mires-fastapi` ([SKILL.md](../mires-fastapi/SKILL.md)).

## SQLAlchemy

SQLAlchemy session, model, and query boundary guidance for repositories that already use SQLAlchemy.

### When To Use

Use when the repository already uses SQLAlchemy and the change touches models, sessions, queries, or transaction boundaries.

### Core Rules

- Reuse the existing engine and session lifecycle.
- Match the repo's sync or async SQLAlchemy style.
- Keep persistence details aligned with the surrounding service boundary.

### Preferred Patterns

- Centralized session creation.
- Model and query code near the existing ownership boundary.
- Focused migrations or schema changes matched to local tooling.

### Anti-Patterns

- Creating a second engine or session factory.
- Mixing sync and async session usage in the same path without precedent.
- Pushing business logic into persistence helpers.

### Checklist

- Confirm the current session lifecycle.
- Confirm where models and queries live today.
- Reuse the migration and validation workflow already in the repo.

---

### SQLAlchemy Session And Model Boundaries

- Reuse the existing engine and session factory.
- Match the repository's sync or async session style.
- Keep query and model changes close to the existing ownership boundary.
- Avoid adding a second persistence abstraction unless the repo already uses one.

#### Async Helper Shape

When a project already uses async SQLAlchemy, keep engine construction and session creation centralized. Dispose app- or worker-lifetime engines explicitly:

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@asynccontextmanager
async def get_engine(*, postgres_uri: PostgresDsn) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(str(postgres_uri), pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@asynccontextmanager
async def get_session(
    *,
    engine: AsyncEngine,
    expire_on_commit: bool = False,
) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=expire_on_commit)
    async with session_factory() as session:
        yield session
```

## Postgres

Postgres and migration guidance for repositories that already use Postgres-related patterns.

### When To Use

Use when the repository already uses Postgres and the change touches schema design, migrations, or Postgres-specific features.

### Core Rules

- Follow the existing migration tool and lifecycle.
- Keep schema changes aligned with the repo's ORM and service boundaries.
- Use Postgres-specific features only when the repo already embraces them or the need is clear.

### Preferred Patterns

- Incremental schema changes.
- Migration files reviewed alongside model changes.
- Postgres-aware indexing and data-shape decisions.

### Anti-Patterns

- Introducing a new migration path.
- Using advanced Postgres features without checking local precedent.
- Coupling migration strategy to one-off feature code.

### Checklist

- Confirm the migration tool and workflow.
- Confirm the touched schema owners.
- Validate migrations and affected queries.

---

### Postgres Patterns

Use this section when changing database models, queries, transactions, or Postgres-backed application state.

For FastAPI engine and session wiring, apply FastAPI SQLAlchemy Connection Setup above. For schema migrations, continue to Alembic Patterns later in this document.

#### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing ORM style, sync versus async access, model base classes, migration pattern, settings source, and transaction boundaries override the examples below.

#### Model Rules

- Use SQLAlchemy 2.x `Mapped[...]` and `mapped_column(...)`.
- Put shared id and timestamp fields on `Base`.
- Add `__tablename__` explicitly for every model.
- Use `ForeignKey(...)` plus `relationship(..., back_populates=...)` on both sides.
- Use `TYPE_CHECKING` imports for relationship-only type hints to avoid import cycles.
- Keep enum status columns backed by the shared `ProcessingStatus` when they represent background work.
- Add indexes or unique constraints on natural lookup keys such as SKU and normalized names.
- Do not call `Base.metadata.create_all()` for app startup. Use Alembic.

#### pgvector Rules

- Keep vector dimension tied to `settings.EMBEDDING_DIMENSION`.
- Ensure an Alembic migration creates the `vector` extension before tables with vector columns.
- Store embeddings on the model that owns similarity behavior.
- When changing embedding dimensions, treat it as a data migration concern, not only a model edit.

#### Transaction Rules

- Use one request-scoped `AsyncSession` for API handlers.
- Use `async with db.get_session(engine=engine) as session, session.begin():` for service workflows that own their transaction.
- Use `flush()` and `refresh()` when generated ids are needed before returning or relating objects.
- Commit processing rows before enqueueing background tasks.
- Worker services should open their own session from a worker-local engine.

#### Query Rules

- Prefer `select(Model)` and `await session.execute(...)` or `await session.scalars(...)`.
- Use `selectinload(...)` for relationships returned through API responses.
- Avoid lazy-load surprises in response serialization. Load relationships before building nested Pydantic responses.

#### Review Checklist

- Model changes have matching Alembic migrations.
- New foreign keys have relationships and back-populates where useful.
- Background workflows persist `pending`, `processing`, `completed`, and `failed` states consistently.
- Vector extension and vector columns are ordered correctly in migrations.
- Tests or manual verification cover transaction boundaries for status updates.

---

### Alembic Patterns

Use this section when adding migrations, reviewing migration output, or changing Alembic configuration.

Review Postgres Patterns above before changing model design. For local infrastructure needed to run migrations, apply the Docker Compose sections earlier in this `SKILL.md`.

#### Migration Workflow

1. Update SQLAlchemy models.
2. Start local database infrastructure with the repository's established command.
3. Create a migration with the repository's command or `uv run alembic revision --autogenerate -m "<change>"`.
4. Inspect the generated file before applying it.
5. Adjust extension ordering, enum handling, indexes, constraints, and downgrades manually.
6. Apply with the repository's command or `uv run alembic upgrade head`.
7. Verify state with `uv run alembic current` or `uv run alembic history`.

#### Async Env Rules

- Keep Alembic's URL sourced from settings so migrations use the same `.env` contract as the app.
- Keep all model imports reachable before `target_metadata = Base.metadata`.
- Use `async_engine_from_config(...)` for asyncpg URLs and run migrations through `connection.run_sync(...)`.
- Use `pool.NullPool` for migration engines.
- Do not create an app engine from `src/db/database.py` inside Alembic env; Alembic owns its migration engine.

#### Autogenerate Review Rules

- Autogenerate is a draft. Always inspect the migration.
- Preserve extension migrations before vector columns.
- Check enum changes carefully. Postgres enum alterations often need manual SQL.
- Check downgrade order: drop dependent join tables before parent tables.
- Check indexes and unique constraints on lookup fields.
- Keep generated imports minimal but complete, especially `pgvector`.
- Use descriptive migration messages instead of placeholder names when creating new migrations.

#### pgvector Rules

- Create the extension with `CREATE EXTENSION IF NOT EXISTS vector`.
- Do not drop the extension in a downgrade if existing data or other tables may still depend on it, unless the migration is clearly isolated and safe.
- If changing `settings.EMBEDDING_DIMENSION`, plan how existing vector data will be rewritten or discarded.

#### Checklist

- `alembic/env.py` still imports all models and points at `Base.metadata`.
- Migration applies against a fresh local Postgres database.
- Migration applies after the current head.
- Downgrade is present and ordered.
- pgvector extension and vector columns are ordered correctly.
- The repository's established migration command remains documented as the entrypoint.

## Celery

Celery task, worker, queue, and worker-testing guidance for repositories that already use Celery-style job processing.

### When To Use

Use when the change touches background tasks, workers, retries, queue routing, or Celery-backed testing.

### Core Rules

- Keep business logic out of task wrappers.
- Reuse the existing worker app and broker setup.
- Pass small serializable task payloads.

### Preferred Patterns

- Thin task wrappers around service functions.
- Explicit queue and retry behavior.
- Focused worker tests when background execution matters.

### Anti-Patterns

- Hiding core logic in task functions.
- Creating a second Celery app without local precedent.
- Passing request-scoped or framework objects into tasks.

### Checklist

- Confirm the current worker app and broker pattern.
- Confirm where task registration lives.
- Validate enqueue and worker execution paths that changed.

---

### Celery App Setup

Use this section when adding or reviewing standalone Celery app setup, broker configuration, task registration, worker resource scope, or queue behavior.

#### Convention Priority

Run project-conventions discovery before applying this skill to an existing repository. Existing Celery app location, settings pattern, broker configuration, task registration, worker resource lifecycle, and service boundaries override the examples below.

#### Preferred Shape

```python
from celery import Celery

from src.config import settings
from src.services.broker import broker_transport_options


app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=None,
)
app.conf.update(broker_transport_options=broker_transport_options())
app.set_default()
app.autodiscover_tasks()

from src import tasks  # noqa: E402,F401
```

```python
import asyncio

from celery import shared_task

from src.config import settings
from src.db import database as db
from src.my_domain import services


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

When a task needs external clients, create them inside the task wrapper and pass them into the service with scalar ids. Do not pass request sessions, ORM objects, or SDK clients through the broker message:

```python
@shared_task
def import_items_task(processing_id: int, file_id: int, source_id: int) -> None:
    async def run() -> None:
        s3_client = boto3.client("s3", **get_s3_client_kwargs())
        embedding_client = get_embedding_client()
        llm_client = get_llm_client()

        async with db.get_engine(postgres_uri=settings.POSTGRES_URI) as engine:
            await import_items(
                processing_id=processing_id,
                file_id=file_id,
                source_id=source_id,
                engine=engine,
                s3_client=s3_client,
                embedding_client=embedding_client,
                llm_client=llm_client,
            )

    asyncio.run(run())
```

#### Rules

- Keep Celery configuration in one module. Do not scatter broker setup across tasks or services.
- Use a settings-driven broker URL and typed settings fields.
- Do not add a result backend unless the app reads task results from Celery. Prefer domain status rows for user-visible progress.
- Keep broker-specific kwargs in helper functions so changing brokers does not leak transport details into tasks.
- Call `app.set_default()` before relying on `@shared_task` task registration.
- Import or autodiscover task modules after the app is configured.
- Keep task wrappers thin: create resources, open engine or session scope, call one service.
- Keep services independent of Celery so they are directly testable.
- Pass only serializable primitives in task messages.
- Create external API clients once per task and pass them into services when needed.

#### Anti-Patterns

- Do not put business workflows directly in task functions.
- Do not import FastAPI `app`, `Request`, or dependencies inside task wrappers.
- Do not pass ORM objects, SQLAlchemy sessions, boto clients, file handles, or request bodies with unbounded size through Celery.
- Do not copy SQS `broker_transport_options` into Redis projects.
- Do not assume task result backend state is the source of truth when the domain has explicit processing tables.
- Do not create hidden task imports that depend on application startup side effects.

---

### Celery Testing

Use this section when writing fast tests for services, FastAPI routes, Celery task wrappers, or broker-free background job behavior.

For tests that must prove `.delay()` or `.apply_async()` reaches a real broker and worker, continue to Celery Live Worker Testing later in this document.

#### Test Layers

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
   - If the worker must consume from the broker, switch to the Celery Live Worker Testing section below.

#### Minimal Examples

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

#### Rules

- Configure pytest with async mode enabled for async FastAPI and SQLAlchemy code.
- Test status transitions, not only task enqueue calls.
- Use fakes for external APIs and clients by default.
- Keep task tests focused on wiring. Put behavior assertions in service tests.
- Add at least one failure-path test that proves status becomes `FAILED` when a service raises after processing starts.
- Add migration smoke tests when task tables or status enums change.
- Keep real broker and worker checks in a small `@pytest.mark.integration` live-worker suite.

#### Anti-Patterns

- Do not make every test require a live broker.
- Do not assert Celery internals when the contract is route enqueues task with ids.
- Do not test async services only through Celery; it slows feedback and hides service errors.
- Do not use production `.env` values in tests.
- Do not rely on task result backend state unless the application explicitly uses a result backend.
- Do not rely on `task_always_eager` when the goal is to prove real worker behavior.

---

### Celery Live Worker Testing

Use this section for integration tests that must prove the real Celery execution path works:

```text
FastAPI route or service -> task.delay/apply_async -> broker -> worker -> task -> service -> database update
```

This is not the default test layer. Keep these tests few, focused, and marked as integration.

#### When to Use

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

#### Test Strategy

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

#### Pytest Setup

Install Celery pytest support:

```bash
uv add --dev "celery[pytest]"
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

#### Celery Test Configuration

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

#### Minimal Worker Check

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

#### FastAPI Flow Pattern

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

#### Polling Helper

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

#### Task Design for Testability

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

#### Docker Smoke Tests

Use `pytest-celery` only for production-like smoke tests that need Docker-based infrastructure, such as worker container startup, app-to-broker publishing, expected queue consumption, and production Celery config loading. Keep these tests very few.

#### Rules

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

#### Anti-Patterns

- Do not make every test require Redis, RabbitMQ, or a Celery worker.
- Do not test all business rules through Celery.
- Do not pass ORM objects to tasks.
- Do not use production `.env` values.
- Do not rely on `task_always_eager` when the goal is to prove real worker behavior.
- Do not assert private Celery internals.
- Do not use fixed long sleeps when polling is possible.
- Do not hide worker errors by only asserting the HTTP response.
- Do not use the result backend as the source of truth unless the application uses it directly.
