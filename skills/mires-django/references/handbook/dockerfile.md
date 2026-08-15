# Production Container

## Purpose and when to use it

Use this multi-stage image for a reconstructed synchronous REST service.

## When not to use it

Realtime deployments use the same image with the Daphne command documented by the realtime recipe.

## Responsibilities and invariants

Dependencies are installed from the frozen lock, the process runs as an unprivileged user, and source is copied only after dependency installation.

## Complete canonical artifact

<!-- artifact: Dockerfile; profiles: base -->
```dockerfile
FROM ghcr.io/astral-sh/uv:0.11.32 AS uv

FROM python:3.14.4-slim-bookworm AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14.4-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src /app/src
COPY --chown=app:app gunicorn.conf.py /app/gunicorn.conf.py
USER app
EXPOSE 8000
CMD ["gunicorn", "--chdir", "/app/src", "--config", "/app/gunicorn.conf.py", "core.wsgi:application"]
```

## Alternatives and trade-offs

A distro-managed Python image is larger but easier to inspect than a distroless runtime.

## Required tests

Build the image, run as the configured user, execute Django deploy checks, and smoke-test liveness.

## Related standards

See [Gunicorn](gunicorn.conf.md) and [operations](docs/operations.md).
