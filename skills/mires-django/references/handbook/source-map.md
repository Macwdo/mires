# Original Source Map

## Purpose

This ledger accounts for every one of the 91 paths tracked by the executable
repository before its conversion to a Markdown-only standards handbook. Each
original path appears exactly once.

The allowed dispositions are:

- **converted**: the implementation keeps a path-shaped Markdown standard;
- **merged into an index**: an empty package marker is represented by its
  directory handbook index;
- **safely replaced**: the old concern is covered by a safer or more generic
  standard at a different path;
- **removed as empty/generated**: an empty placeholder or retired generated
  fixture has no canonical implementation;
- **generated at reconstruction**: an ordinary schema migration is mechanically
  derivable from its app's models and is produced by running `makemigrations`
  against a materialized profile rather than carried as a canonical artifact;
  see [reconstruction](docs/reconstruction.md#migration-generation).

Cookiecutter generation is retired. Its fixtures are not active commands or
templates. The former `.env.local` is safely replaced by the placeholder-only
`.env.example` artifact in `environment.md`; no secret or local value was
copied.

## Path accounting

| # | Original tracked path | Disposition | Handbook location or rationale |
| ---: | --- | --- | --- |
| 1 | `.env.local` | safely replaced | `environment.md` documents a placeholder-only `.env.example` artifact |
| 2 | `.gitignore` | converted | `gitignore.md` |
| 3 | `.pre-commit-config.yaml` | converted | `pre-commit-config.md` |
| 4 | `.python-version` | converted | `python-version.md` |
| 5 | `.vscode/launch.json` | converted | `.vscode/launch.md` |
| 6 | `.vscode/settings.json` | converted | `.vscode/settings.md` |
| 7 | `CLAUDE.md` | safely replaced | `maintainer-instructions.md` is the tool-neutral contribution and agent guide |
| 8 | `Dockerfile` | converted | `dockerfile.md` |
| 9 | `Makefile` | converted | `makefile.md` |
| 10 | `README.md` | converted | `README.md` is the handbook entry point |
| 11 | `conftest.py` | converted | `conftest.md` |
| 12 | `docker-compose-dev.yml` | converted | `compose-dev.md` |
| 13 | `docker-compose.yml` | converted | `compose.md` |
| 14 | `gunicorn.conf.py` | converted | `gunicorn.conf.md` |
| 15 | `pyproject.toml` | converted | `pyproject.md` |
| 16 | `pytest.ini` | converted | `pytest.md` |
| 17 | `scripts/channels-worker.sh` | converted | `scripts/channels-worker.md` |
| 18 | `scripts/channels.sh` | converted | `scripts/channels.md` |
| 19 | `scripts/webserver.sh` | converted | `scripts/webserver.md` |
| 20 | `scripts/worker.sh` | converted | `scripts/worker.md` |
| 21 | `src/apps/__init__.py` | merged into an index | `src/apps/README.md` |
| 22 | `src/apps/account/__init__.py` | merged into an index | `src/apps/account/README.md` |
| 23 | `src/apps/account/admin.py` | converted | `src/apps/account/admin.md` |
| 24 | `src/apps/account/apps.py` | converted | `src/apps/account/apps.md` |
| 25 | `src/apps/account/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 26 | `src/apps/account/migrations/0002_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 27 | `src/apps/account/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 28 | `src/apps/account/models.py` | converted | `src/apps/account/models.md` |
| 29 | `src/apps/account/services.py` | converted | `src/apps/account/services.md` |
| 30 | `src/apps/account/tests.py` | removed as empty/generated | Empty placeholder superseded by focused test modules |
| 31 | `src/apps/account/views.py` | removed as empty/generated | Empty placeholder; account behavior is exposed through authentication and scoped resources |
| 32 | `src/apps/api/__init__.py` | merged into an index | `src/apps/api/README.md` |
| 33 | `src/apps/api/apps.py` | converted | `src/apps/api/apps.md` |
| 34 | `src/apps/api/conftest.py` | removed as empty/generated | Empty placeholder; shared fixtures live in `src/apps/conftest.md` |
| 35 | `src/apps/api/exceptions.py` | converted | `src/apps/api/exceptions.md` |
| 36 | `src/apps/api/health.py` | converted | `src/apps/api/health.md` |
| 37 | `src/apps/api/pagination.py` | converted | `src/apps/api/pagination.md` |
| 38 | `src/apps/api/tests/__init__.py` | merged into an index | `src/apps/api/tests/README.md` |
| 39 | `src/apps/api/tests/views/test_auth_urls.py` | removed as empty/generated | Route-name assertions duplicated Django's resolver behavior without testing an application outcome |
| 40 | `src/apps/api/tests/views/test_health.py` | converted | `src/apps/api/tests/views/test_health.md` |
| 41 | `src/apps/api/urls.py` | converted | `src/apps/api/urls.md` |
| 42 | `src/apps/api/views.py` | converted | `src/apps/api/views.md` |
| 43 | `src/apps/authentication/__init__.py` | merged into an index | `src/apps/authentication/README.md` |
| 44 | `src/apps/authentication/admin.py` | converted | `src/apps/authentication/admin.md` |
| 45 | `src/apps/authentication/apps.py` | converted | `src/apps/authentication/apps.md` |
| 46 | `src/apps/authentication/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 47 | `src/apps/authentication/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 48 | `src/apps/authentication/models.py` | converted | `src/apps/authentication/models.md` |
| 49 | `src/apps/authentication/serializers.py` | converted | `src/apps/authentication/serializers.md` |
| 50 | `src/apps/authentication/services.py` | converted | `src/apps/authentication/services.md` |
| 51 | `src/apps/authentication/tests/__init__.py` | merged into an index | `src/apps/authentication/tests/README.md` |
| 52 | `src/apps/authentication/tests/helpers.py` | converted | `src/apps/authentication/tests/helpers.md` |
| 53 | `src/apps/authentication/tests/test_me.py` | converted | `src/apps/authentication/tests/test_me.md` |
| 54 | `src/apps/authentication/tests/test_meta.py` | safely replaced | `src/apps/authentication/tests/test_tokens.md` names and tests the JWT lifecycle behavior directly |
| 55 | `src/apps/authentication/tests/test_register.py` | converted | `src/apps/authentication/tests/test_register.md` |
| 56 | `src/apps/authentication/urls.py` | converted | `src/apps/authentication/urls.md` |
| 57 | `src/apps/authentication/views.py` | converted | `src/apps/authentication/views.md` |
| 58 | `src/apps/common/__init__.py` | merged into an index | `src/apps/common/README.md` |
| 59 | `src/apps/common/apps.py` | converted | `src/apps/common/apps.md` |
| 60 | `src/apps/common/exceptions.py` | converted | `src/apps/common/exceptions.md` |
| 61 | `src/apps/common/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 62 | `src/apps/common/models.py` | converted | `src/apps/common/models.md` |
| 63 | `src/apps/common/serializers.py` | removed as empty/generated | Empty placeholder; serializers remain within their owning applications |
| 64 | `src/apps/common/tests.py` | removed as empty/generated | Empty placeholder; tests remain within their owning applications |
| 65 | `src/apps/conftest.py` | converted | `src/apps/conftest.md` |
| 66 | `src/apps/customer/__init__.py` | merged into an index | `src/apps/customer/README.md` |
| 67 | `src/apps/customer/admin.py` | converted | `src/apps/customer/admin.md` |
| 68 | `src/apps/customer/apps.py` | converted | `src/apps/customer/apps.md` |
| 69 | `src/apps/customer/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 70 | `src/apps/customer/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 71 | `src/apps/customer/models.py` | converted | `src/apps/customer/models.md` |
| 72 | `src/apps/customer/serializers.py` | converted | `src/apps/customer/serializers.md` |
| 73 | `src/apps/customer/services.py` | converted | `src/apps/customer/services.md` |
| 74 | `src/apps/customer/tests/__init__.py` | merged into an index | `src/apps/customer/tests/README.md` |
| 75 | `src/apps/customer/tests/helpers.py` | converted | `src/apps/customer/tests/helpers.md` |
| 76 | `src/apps/customer/tests/test_views.py` | converted | `src/apps/customer/tests/test_views.md` |
| 77 | `src/apps/customer/urls.py` | converted | `src/apps/customer/urls.md` |
| 78 | `src/apps/customer/views.py` | converted | `src/apps/customer/views.md` |
| 79 | `src/core/__init__.py` | converted | `src/core/__init__.md` |
| 80 | `src/core/asgi.py` | converted | `src/core/asgi.md` |
| 81 | `src/core/celery.py` | converted | `src/core/celery.md` |
| 82 | `src/core/settings.py` | converted | `src/core/settings/README.md` (split into a settings package; see `src/core/settings/*.md`) |
| 83 | `src/core/urls.py` | converted | `src/core/urls.md` |
| 84 | `src/core/wsgi.py` | converted | `src/core/wsgi.md` |
| 85 | `src/manage.py` | converted | `src/manage.md` |
| 86 | `tests/conftest.py` | converted | `tests/conftest.md` |
| 87 | `tests/fixtures/cookiecutter-basic/cookiecutter.json` | safely replaced | `docs/reconstruction.md` defines profile reconstruction without templates |
| 88 | `tests/fixtures/cookiecutter-basic/{{cookiecutter.project_slug}}/README.md` | safely replaced | `docs/reconstruction.md` defines safe derived output without template variables |
| 89 | `tests/test_healthcheck.py` | converted | `tests/test_healthcheck.md` |
| 90 | `todo.md` | safely replaced | `README.md` navigation and `docs/testing.md` acceptance criteria replace the placeholder list |
| 91 | `uv.lock` | converted | `uv-lock.md` |

## Verification

Compare the second column of the table with the frozen original path list. The
set must match exactly, with 91 table rows, no duplicate original path, and no
omission. Repository validation also confirms that each listed handbook
location is either present or intentionally described as removed.
