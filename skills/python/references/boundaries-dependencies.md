---
name: boundaries-dependencies
description: "Mires Python boundary and dependency-injection guidance. Use when separating core logic from I/O, external clients, framework adapters, environment access, and global construction."
---

# Python Boundaries Dependencies

Use this skill when code touches external services, repositories, clients, framework adapters, or environment configuration.

## Rules

- Pass external clients, repositories, and configurable collaborators into functions instead of constructing them deep inside business logic.
- Keep I/O, network calls, filesystem access, framework adapters, and environment reads at module boundaries.
- Keep core logic testable without booting a framework or patching module globals.
- Use dependency functions at the edge when callers need SDK clients or app settings.
- Prefer explicit collaborators over implicit singletons.

## Example

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

Apply the same boundary to HTTP clients. Return a configured client from an adapter function, then pass it into the service or manage it with `async with` at the call site:

```python
import httpx


def http_client_kwargs() -> dict[str, float]:
    return {"timeout": 10.0}


def get_async_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(**http_client_kwargs())
```
