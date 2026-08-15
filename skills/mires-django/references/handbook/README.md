# Django Backend/API Standards

This repository is an English, Markdown-only handbook for building pragmatic Django backends and APIs. Markdown is the canonical source: complete fenced artifacts can be reconstructed into disposable, tested projects without committing generated code here.

The reference snapshot is Python 3.14.6, Django 6.0.7, and Django REST framework 3.17.1. Versions are intentionally frozen for the 2026-07-26 handbook snapshot; review upstream compatibility before advancing them.

## Start here

- [Architecture](docs/architecture.md) explains boundaries and the two supported application styles.
- [Conventions](docs/conventions.md) defines naming, services, selectors, typing, migrations, and dependency rules.
- [API design](docs/api-design.md) covers JWT, error envelopes, request IDs, throttling, filtering, and cursor pagination.
- [Security](docs/security.md) covers tenant isolation, production validation, credentials, and upload controls.
- [Testing](docs/testing.md) defines the required test pyramid and acceptance matrix.
- [Operations](docs/operations.md) compares WSGI and ASGI deployment and describes health checks.
- [Reconstruction](docs/reconstruction.md) documents the artifact protocol and embeds the `reconstruct` utility.
- [Source map](source-map.md) accounts for all 91 files in the retired executable snapshot.
- [Base reference tree](src/README.md) mirrors a generic Account/Customer API.
- [Recipes](recipes/README.md) — small composable modules for Celery, object storage, realtime delivery, vectors, optional AI, and Sentry.

## Reconstruction

Extract the `reconstruct` artifact from [docs/reconstruction.md](docs/reconstruction.md) to a temporary executable, then run either a legacy alias:

```text
reconstruct --profile base|tasks|storage|realtime|vector-ai|full --output ABSOLUTE_PATH
```

or any explicit combination of the finer-grained modules documented in [recipes](recipes/README.md), mixed freely with aliases:

```text
reconstruct --modules celery-django,sentry-django,storage-s3-core --output ABSOLUTE_PATH
```

The destination must be an explicit, empty absolute directory. The utility rejects traversal, duplicate profile artifacts, malformed fences, and conflicting targets. It never writes generated files into this repository.

<!-- artifact: README.md; profiles: base -->
```markdown
# Generic Django Standard API

This derived teaching project demonstrates an account-scoped Django 6 and Django REST framework API. It contains email authentication, hardened JWT refresh rotation, layered API throttling, Customer CRUD, request IDs, error envelopes, health checks, admin, migrations, and tests.

The generated tree is disposable. Review the handbook standards and adapt the design deliberately before using it in a real service.

## Verify

~~~text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run coverage run -m pytest
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
~~~
```

## Non-goals

This is not an active project generator, a framework layered over Django, or a production API contract. It does not prescribe repositories or use-case classes. Server-rendered templates and forms are outside scope.

## Repository invariant

Every tracked file ends in `.md`. Files such as `pyproject.md`, `compose.md`, and `src/core/settings/base.md` are readable standards documents whose canonical fences reconstruct their executable counterparts.
