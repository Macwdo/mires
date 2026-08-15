# Python Project Configuration

## Purpose and when to use it

One `base` artifact pins the minimal REST stack and development tools.
Every other module contributes a small dependency-fragment (see
[dependency fragments](docs/reconstruction.md#dependency-fragments)) that
`reconstruct` merges into this file's `dependencies`, `dev`, and
`tool.pytest.ini_options` placeholders for whatever module set was
requested — there is no longer a separate fully-duplicated `pyproject.toml`
per legacy profile. Exact pins make the 2026-07-26 snapshot reviewable;
`uv.lock`, generated once per reconstruction (see
[dependency lock generation](docs/reconstruction.md#dependency-lock-generation)),
remains the installation authority.

## When not to use it

Do not copy the full dependency set into a service that does not use those
capabilities — request only the modules it needs.

## Responsibilities and invariants

Python, Django, DRF, Ruff, and `ty` agree on Python 3.14. Django migrations
are linted for syntax but excluded from style churn. Coverage includes
branches. Every dependency-fragment target must have a matching placeholder
in this artifact, or reconstruction fails fast (see
[reconstruction](docs/reconstruction.md)).

## Complete canonical artifacts

<!-- artifact: pyproject.toml; profiles: base -->
```toml
[project]
name = "django-standard-api"
version = "0.1.0"
description = "Generic account-scoped Django REST API"
readme = "README.md"
requires-python = ">=3.14,<3.15"
dependencies = [
  "Django==6.0.7",
  "django-cors-headers==4.9.0",
  "django-filter==26.1",
  "djangorestframework==3.17.1",
  "djangorestframework-simplejwt==5.5.1",
  "gunicorn==26.0.0",
  "psycopg[binary]==3.3.4",
  "python-decouple==3.8",
  # {{FRAGMENT:dependencies}}
]

[dependency-groups]
dev = [
  "coverage==7.15.2",
  "freezegun==1.5.5",
  "pre-commit==4.6.1",
  "pytest==9.1.1",
  "pytest-django==4.12.0",
  "ruff==0.16.0",
  "ty==0.0.63",
  # {{FRAGMENT:dev}}
]

[tool.uv]
package = false
default-groups = ["dev"]

[tool.ruff]
target-version = "py314"
line-length = 100
src = ["src"]
extend-exclude = [".venv", ".data", "staticfiles", "media"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "DJ", "RUF"]
ignore = ["DJ001"]

[tool.ruff.lint.isort]
known-first-party = ["apps", "core"]

[tool.ruff.lint.per-file-ignores]
"**/migrations/*.py" = ["E501", "RUF012"]
"**/tests/*.py" = ["B011"]
"src/core/settings/__init__.py" = ["F401", "F403"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings"
pythonpath = ["src"]
python_files = ["test_*.py"]
addopts = "-ra --strict-config --strict-markers"
markers = [
  "integration: requires external infrastructure",
  "realtime: exercises ASGI or WebSocket behavior",
]
# {{FRAGMENT:pytest}}

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["*/migrations/*", "*/tests/*", "src/core/*", "src/manage.py"]

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 90
exclude_also = [
  "if TYPE_CHECKING:",
  "if __name__ == .__main__.:",
]
```

## Alternatives and trade-offs

Range constraints reduce update churn but make a handbook snapshot less
reproducible. Upgrade pins deliberately.

Splitting the six duplicated whole-file variants into one base file plus
per-module dependency-fragments removes the drift risk of editing a shared
line (like the `sentry-sdk` pin used to be) in six places; the cost is that
`pyproject.toml` can no longer be read as one flat, complete list without
running `reconstruct` — the fragments must be read alongside their owning
module doc to see the whole picture ahead of generation.

`ty` still has incomplete knowledge of Django's dynamic fields, managers,
and DRF generics. Use narrow suppressions at the dynamic boundary and retain
runtime tests; do not add blanket ignores.

## Required tests

Run frozen sync, Ruff, `ty`, pytest/coverage, Django checks, and the
migration drift check for `base` and `full`. Confirm the merged
`pyproject.toml` for at least one non-alias module combination contains
exactly its resolved modules' dependency-fragments (see
[reconstruction](docs/reconstruction.md#required-tests)).

## Related standards

See [version snapshot](docs/version-snapshot.md), [testing](docs/testing.md),
and [reconstruction](docs/reconstruction.md).
