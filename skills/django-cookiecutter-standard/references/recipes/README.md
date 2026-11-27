# Optional Recipes

Recipes inherit the base project and add one coherent capability, broken
into small composable **modules** with explicit dependency edges (see
[reconstruction](../docs/reconstruction.md) for how requests resolve):

- [Celery](celery/README.md) — `celery-core`, `celery-redis-broker`,
  `celery-postgres-results`, `celery-django`, `celery-beat`.
- [Storage](storage/storage-s3-core.md) — `storage-s3-core`,
  [`storage-django`](storage/storage-django.md).
- Realtime — [SSE](sse.md) (`realtime-sse`) and [Channels](channels.md)
  (`realtime-channels`), independent of each other.
- Vector/AI — [pgvector](vector.md) (`vector-pgvector`),
  [OpenAI and Deep Agents](openai-deep-agents.md) (`vector-ai-openai`), and
  [chat streaming](chat.md) (`chat-streaming`).
- [Sentry](sentry/README.md) — `sentry-python`, `sentry-django`.
- [Advanced tenancy](tenancy.md) — `tenancy-advanced`.
- [Deployment comparison](deployment.md) — not a module; documents WSGI vs.
  ASGI trade-offs across every module combination.

The legacy `tasks`, `storage`, `realtime`, `vector-ai`, and `full` names
still work as aliases that expand to a fixed module set — see the alias
table in [reconstruction](../docs/reconstruction.md). Request individual
modules directly (`--modules celery-django,sentry-django`) for combinations
the six original profiles could never express. Choose modules because the
product needs them; `full` is an integration teaching project, not a
recommendation to install everything.

Each module states when the added infrastructure is justified, owns only
its feature-level canonical artifacts, and lists the integration and
failure cases that must be tested. Project aggregators such as settings,
URLs, dependency locks, Compose, and core ASGI/Celery entry points remain
owned by their top-level standards so modules cannot silently overwrite one
another.
