# Repository Guidelines

## Project Structure & Module Organization

This is a Markdown-only Django backend/API handbook. `docs/` defines cross-cutting architecture, API, security, testing, operations, and reconstruction standards. `src/core/` and `src/apps/` mirror the base Django reference project; their `.md` files contain complete canonical artifacts. `recipes/` adds optional tasks, storage, realtime, vector, AI, tenancy, and deployment profiles. Root documents describe tooling and infrastructure, while `tests/` and `scripts/` document reconstructed test and process files. Keep `source-map.md` aligned with all 91 paths from the retired executable repository.

## Build, Test, and Development Commands

Extract the utility embedded in `docs/reconstruction.md`, then materialize a profile only into an empty directory outside this repository:

```text
reconstruct --profile base --output /tmp/django-standard-base
```

Inside a reconstructed `base` or `full` project, run:

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

Before handoff, validate all six profiles as described in `docs/testing.md`, then run `git diff --check` and `git status --short`.

## Coding Style & Naming Conventions

Every tracked file must end in `.md`. Use concise English, ATX headings, repository-relative links, and fenced languages matching artifact target types. Canonical markers must immediately precede one complete fence:

```markdown
&lt;!-- artifact: src/apps/customer/models.py; profiles: base,full --&gt;
```

Never use ellipses in canonical code. Prefer direct Django/DRF CRUD; use services for transactions or effects and selectors for reusable complex reads. Do not introduce repository or use-case layers.

## Cross-App Boundaries

Every app under `src/apps/` owns its models privately. When one app's functionality is consumed by another app (for example, an AI/assistant app calling into a domain app's data), apply these rules to every new artifact:

- Define a `dtos.py` in the owning app with `pydantic.BaseModel` classes for any function whose parameters or return value would otherwise be a model instance, a queryset, or more than two or three plain parameters. Prefer one DTO parameter over a long keyword-argument list.
- A service or selector meant to be called from another app returns DTOs, never a model instance or `QuerySet`. Same-app callers (a ViewSet, a serializer, a test in that app) may still use the app's own models and querysets directly; the DTO boundary applies at the point another app imports from this one.
- The consuming app imports only `dtos.py` and the specific service/selector functions it needs (e.g. `from apps.<owner>.dtos import WidgetDTO` and `from apps.<owner>.services import list_widgets`). It must never import `models.py`, build a `QuerySet`, or otherwise reach into another app's internals.
- Name a cross-app read entry point after what it returns (e.g. `list_widgets`), not after its storage shape, and keep it in the owning app's `services.py` or `selectors.py`.
- This rule governs the shape of any new cross-app artifact; it does not itself require adding a new domain app. `customer` remains the handbook's only CRUD teaching app.

## Testing Guidelines

Use pytest with files named `test_*.py` in reconstructed projects. Maintain at least 90% coverage for `base` and `full`. Follow Arrange, Act, Assert in that order; treat `pytest.raises` as an assertion and establish all inputs before it. Test tenant isolation, authorization failures, migrations, health checks, and each affected recipe. Avoid tests that only restate framework behavior, settings, route registration, or internal call shapes. Use deterministic mocks for vendor APIs; never require real credentials.

## Commit & Pull Request Guidelines

History follows Conventional Commit prefixes such as `feat:` and `chore:` with short imperative summaries. Keep commits focused. Pull requests should explain the standard changed, affected profiles, reconstruction results, and security or migration implications; link relevant issues and include rendered-document screenshots only when formatting materially changes.

## Security & Agent Instructions

Never commit secrets, reconstructed output, generated code, or product-specific data. Scope every account-owned query before lookup or mutation. Do not run destructive database, bucket, or worktree commands without explicit authorization.

## Knowledge Graph

This repository has a graphify knowledge graph in `graphify-out/`. Before exploring the codebase manually for an architecture, cross-file, or "how does X relate to Y" question, query it first:

```text
graphify query "<question>"
```

Fall back to manual exploration only if the graph doesn't have an answer. After adding, removing, or materially changing `.md` files, run `/graphify --update` to keep the graph in sync.
