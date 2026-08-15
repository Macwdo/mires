# Operations

## Purpose and when to use it

Use these deployment patterns after selecting the capabilities the service actually needs.

## WSGI and ASGI

Gunicorn with `core.wsgi` is the conservative default for synchronous REST. It has simple worker behavior and broad operational familiarity.

Daphne with `core.asgi` is required for long-lived async SSE and WebSockets. Channels routes HTTP and WebSocket protocols through `ProtocolTypeRouter`; Redis is the production channel layer. A reverse proxy may route ordinary REST to Gunicorn and realtime paths to Daphne, or Daphne may serve both.

Do not run blocking ORM or network work directly on an event loop. Use Django's async-safe interfaces or explicit sync adapters. Never set `DJANGO_ALLOW_ASYNC_UNSAFE` in production.

## Deployment invariants

- Run migrations once as a release job, not concurrently in every web worker.
- When Celery beat is deployed, run `sync_periodic_tasks` in that same release
  job so the database-backed schedule reflects code before beat starts.
- Serve static assets outside application workers.
- Terminate TLS at a trusted proxy and configure forwarded-proto handling.
- Use liveness for process restarts and readiness for traffic admission.
- Gracefully drain workers; reconnecting SSE and WebSocket clients resume from event IDs or application state.
- Send structured JSON logs to stdout and initialize Sentry only when a DSN is configured.

## Required tests

Validate container configuration, production settings, graceful shutdown, health endpoints, migration drift, and one smoke request through the chosen process server.
