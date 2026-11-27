---
name: django-cookiecutter-standard
description: "Django 6 and Django REST framework backend standard from the Macwdo cookiecutter handbook: architecture, conventions, API design, security, testing, operations, and optional recipes. Use when designing, reviewing, or scaffolding a Django/DRF backend that should follow this standard."
---

# Django Cookiecutter Standard

Use this skill as the Markdown handbook for a Django backend/API. The handbook is canonical: every file under `references/` is a standards document, and its fenced `artifact` blocks are complete canonical code that can be reconstructed into a disposable project. Do not treat the handbook as a generator and do not commit generated code back into a project from it.

The reference snapshot is Python 3.14.6, Django 6.0.7, and Django REST framework 3.17.1. Review upstream compatibility before advancing versions.

## When To Use

- Starting or reviewing a Django/DRF API that should match the team's standard.
- Deciding between direct Django/DRF CRUD, services, and selectors.
- Writing JWT auth, error envelopes, throttling, pagination, tenant isolation, or upload controls.
- Adding Celery, object storage, realtime, vector search, Sentry, or tenancy through a recipe.
- Writing tests for a Django/DRF change under this standard.

## Where To Look

Start with `references/README.md`, then open only the document that matches the task:

| Need | Read |
| --- | --- |
| Boundaries and application styles | `references/docs/architecture.md` |
| Naming, services, selectors, typing, migrations | `references/docs/conventions.md` |
| JWT, error envelope, request IDs, throttling, pagination | `references/docs/api-design.md` |
| Tenant isolation, production validation, credentials, uploads | `references/docs/security.md` |
| Test pyramid and acceptance matrix | `references/docs/testing.md` |
| WSGI/ASGI, health checks, deployment | `references/docs/operations.md` |
| Artifact protocol and reconstruction utility | `references/docs/reconstruction.md` |
| Base reference tree (Account/Customer API) | `references/src/README.md` |
| Optional modules (Celery, storage, realtime, vector, AI, Sentry, tenancy) | `references/recipes/README.md` |
| Which of the 91 original files each document covers | `references/source-map.md` |

## Core Rules

- Prefer direct Django/DRF CRUD. Use services for transactions or side effects and selectors for reusable complex reads. Do not add repository or use-case layers.
- Scope every account-owned query before lookup or mutation. Tenant isolation and authorization failures must have tests.
- Every app under `src/apps/` owns its models privately. Cross-app consumers import only the owner's `dtos.py` and its service or selector functions. A cross-app read returns DTOs (`pydantic.BaseModel`), never a model instance or `QuerySet`.
- Name cross-app read entry points after what they return (for example `list_widgets`), not after storage.
- Never commit secrets, real credentials, or environment values.
- Tests use pytest with `test_*.py`, Arrange-Act-Assert order, and deterministic mocks for vendor APIs. Do not write tests that only restate framework behavior, settings, route registration, or internal call shapes.

## Snippet-Driven Implementation

Always select the closest canonical fence from the handbook before generating Django code, then adapt it to the target project.

1. Identify the boundary: model, service, selector, view, serializer, recipe module, or test.
2. Find the matching canonical fence in `references/src/` or `references/recipes/` (fences are preceded by an `artifact:` marker naming the target file).
3. Compare it with the target repository's adjacent implementation.
4. Adapt names, imports, app layout, and dependencies to the target; keep the fence's invariants (ownership, tenant scoping, typing, error shape).
5. When deviating, follow the target repository and state the concrete reason.

Use this trace before implementation:

```text
Boundary: <model, service, selector, view, recipe module, test>
Repository pattern: <nearby file or established abstraction>
Reference fence: <references/... path and artifact marker>
Adaptations: <names, dependencies, Django/DRF version, local conventions>
Verification: <focused test or manage.py check path>
```

## Verify

For a reconstructed `base` or `full` project, run:

```text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run coverage run -m pytest
uv run coverage report --fail-under=90
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
```

Maintain at least 90% coverage for `base` and `full`. Test tenant isolation, authorization failures, migrations, health checks, and each affected recipe.

## References Index

All documents are under `references/`, keeping the handbook's original paths: `docs/`, `recipes/`, `src/`, `tests/`, `scripts/`, and the root documents (`README.md`, `AGENTS.md`, `pyproject.md`, `compose.md`, `environment.md`, and so on).
