---
name: mires-django
description: Apply Macwdo's opinionated Django and Django REST framework standards from an executable Markdown handbook. Use for Django project architecture, models, services, selectors, serializers, APIs, migrations, testing, security, operations, Celery, storage, realtime, vectors, tenancy, AI integrations, or reconstructing a reference project.
---

# Mires Django

Use this optional Mires companion after inspecting the target repository. Existing project conventions take precedence; use the bundled handbook to fill genuine gaps, implement new boundaries, or review decisions.

## Start With The Task

1. Read `references/handbook/docs/architecture.md` and `references/handbook/docs/conventions.md` for cross-cutting design work.
2. Read only the documents and canonical artifacts relevant to the requested boundary.
3. Record the target repository's configuration, database/session, dependency injection, service/repository, error, testing, naming, and module patterns before backend implementation.
4. Adapt the reference instead of copying product-specific assumptions.
5. Run the target repository's checks; reconstruct a handbook profile only when validating the reference itself.

## Route By Boundary

- API contracts, authentication, errors, throttling, filtering, and pagination: `references/handbook/docs/api-design.md`
- Security, tenant isolation, uploads, credentials, and production validation: `references/handbook/docs/security.md`
- Test strategy and acceptance matrix: `references/handbook/docs/testing.md`
- WSGI, ASGI, health checks, and deployment: `references/handbook/docs/operations.md`
- Models, serializers, selectors, services, views, and URLs: `references/handbook/src/apps/README.md`
- Settings, startup, Celery, and framework entrypoints: `references/handbook/src/core/README.md`
- Optional capabilities: inspect `references/handbook/recipes/README.md`, then load only the selected recipe.
- Exact version snapshot: `references/handbook/docs/version-snapshot.md`
- Disposable reference generation: `references/handbook/docs/reconstruction.md`

## Preserve The Handbook Contract

- Treat the bundled Markdown as reference source, not as code to paste blindly.
- Do not commit reconstructed output.
- Keep account-owned queries scoped before lookup or mutation.
- Prefer direct Django and DRF patterns; use services for transactions or effects and selectors for reusable complex reads.
- Do not introduce repository or use-case layers unless the target repository already owns them.
- Keep cross-app model access behind explicit DTO and service or selector boundaries.

## Source

Read `references/source.md` for provenance and synchronization instructions. This is a standards handbook with reconstructable examples, not an active cookiecutter or project generator.
