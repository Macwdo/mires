# Project Commands

## Purpose and when to use it

The reconstructed Makefile provides memorable local commands while keeping the underlying commands visible.

## Complete canonical artifact

<!-- artifact: Makefile; profiles: base -->
```makefile
SHELL := /bin/sh
UV_RUN := uv run
COMPOSE := docker compose

.PHONY: sync format lint typecheck test coverage check migrations-check run migrate superuser compose-config

sync:
	uv sync --frozen

format:
	$(UV_RUN) ruff format .

lint:
	$(UV_RUN) ruff format --check .
	$(UV_RUN) ruff check .

typecheck:
	$(UV_RUN) ty check

test:
	$(UV_RUN) pytest

coverage:
	$(UV_RUN) coverage run -m pytest
	$(UV_RUN) coverage report --fail-under=90

check:
	$(UV_RUN) python src/manage.py check

migrations-check:
	$(UV_RUN) python src/manage.py makemigrations --check --dry-run

run:
	$(UV_RUN) python src/manage.py runserver 0.0.0.0:8000

migrate:
	$(UV_RUN) python src/manage.py migrate

superuser:
	$(UV_RUN) python src/manage.py createsuperuser

compose-config:
	$(COMPOSE) config
```

## Responsibilities and invariants

Commands do not rewrite migrations, erase databases, buckets, or volumes, and do not hide environment selection.

## Required tests

Run every read-only validation target in CI.
