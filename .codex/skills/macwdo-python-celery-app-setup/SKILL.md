---
name: macwdo-python-celery-app-setup
description: Macwdo's Celery app and worker setup pattern for Python and FastAPI repos. Use for Celery app modules, settings-driven broker configuration, Redis or SQS transport options, set_default and task registration, shared_task wrappers, worker resource scope, async service bridging, and keeping business logic outside tasks.
---

# Celery App Setup

Use this skill when adding or reviewing standalone Celery app setup, broker configuration, task registration, worker resource scope, or queue behavior.

## Source Repo Signals

- Celery app setup is centralized in `src/celery_app.py` with a named app, settings-driven broker URL, and no result backend: `src/celery_app.py:6`.
- Broker-specific transport options are isolated behind helper functions: `src/celery_app.py:12`, `src/services/aws.py:17`.
- The app is made default and tasks are discovered or imported after configuration: `src/celery_app.py:18`, `src/celery_app.py:19`, `src/celery_app.py:21`.
- Tasks are registered with `@shared_task`: `src/tasks.py:17`, `src/tasks.py:26`.
- Sync Celery task functions call async services with nested async runners and `asyncio.run(...)`: `src/tasks.py:19`, `src/tasks.py:23`, `src/tasks.py:32`, `src/tasks.py:48`.
- Worker tasks create worker-local external clients and database engines before delegating to services: `src/tasks.py:33`, `src/tasks.py:34`, `src/tasks.py:35`, `src/tasks.py:37`.
- Worker startup is documented as `uv run celery -A src.celery_app.app worker --loglevel=INFO`: `README.md:194`.

## Preferred Shape

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

## Rules

- Keep Celery configuration in one module. Do not scatter broker setup across tasks or services.
- Use a settings-driven broker URL and typed settings fields.
- Do not add a result backend unless the app reads task results from Celery. Prefer domain status rows for user-visible progress.
- Keep broker-specific kwargs in helper functions. The source repo uses SQS kwargs through `get_sqs_client_kwargs`; Redis projects should use the same boundary with Redis-specific settings.
- Call `app.set_default()` before relying on `@shared_task` task registration.
- Import or autodiscover task modules after the app is configured.
- Keep task wrappers thin: create resources, open engine or session scope, call one service.
- Keep services independent of Celery so they are directly testable.
- Pass only serializable primitives in task messages.
- Create external API clients once per task and pass them into services when needed.

## Anti-Patterns

- Do not put business workflows directly in task functions.
- Do not import FastAPI `app`, `Request`, or dependencies inside task wrappers.
- Do not pass ORM objects, SQLAlchemy sessions, boto clients, file handles, or request bodies with unbounded size through Celery.
- Do not copy SQS `broker_transport_options` into Redis projects.
- Do not assume task result backend state is the source of truth when the domain has explicit processing tables.
- Do not create hidden task imports that depend on application startup side effects.
