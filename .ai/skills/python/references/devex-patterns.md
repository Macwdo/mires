---
name: devex-patterns
description: Mires's Python developer experience patterns. Use for uv dependency workflows, pyproject configuration, Ruff lint and format rules, pytest async settings, pre-commit hooks, Makefile targets, local setup commands, README run instructions, and keeping tooling consistent with ml-products-grouping.
---

# DevEx Patterns

Use this skill when changing project tooling, local commands, README setup instructions, or test/lint configuration.

## Source Repo Signals

- The project is managed through `pyproject.toml` and `uv.lock`: `pyproject.toml:1`.
- Python requires 3.12 or newer: `pyproject.toml:6`.
- Runtime dependencies include FastAPI, Celery SQS, async SQLAlchemy, Alembic, pgvector, boto3, and LLM tooling: `pyproject.toml:8`, `pyproject.toml:11`, `pyproject.toml:12`, `pyproject.toml:18`, `pyproject.toml:23`.
- Dev dependencies include pre-commit, pytest, pytest-asyncio, and Ruff: `pyproject.toml:28`, `pyproject.toml:32`, `pyproject.toml:33`, `pyproject.toml:35`, `pyproject.toml:36`.
- Ruff is configured in `pyproject.toml` with Python 3.13 target, preview mode, and Alembic excluded: `pyproject.toml:40`, `pyproject.toml:43`, `pyproject.toml:53`.
- Pytest uses project-root pythonpath and automatic asyncio mode: `pyproject.toml:88`, `pyproject.toml:89`, `pyproject.toml:91`.
- Pre-commit runs `uv-lock`, `ruff-check`, and `ruff-format`: `.pre-commit-config.yaml:1`, `.pre-commit-config.yaml:5`, `.pre-commit-config.yaml:11`, `.pre-commit-config.yaml:14`.
- The Makefile is the local command surface for setup, pre-commit, Compose, LocalStack provisioning, and Alembic: `Makefile:2`, `Makefile:7`, `Makefile:12`, `Makefile:19`, `Makefile:32`.
- README documents `make setup-project`, `make up`, API startup, and worker startup: `README.md:164`, `README.md:174`, `README.md:188`, `README.md:196`.

## Command Rules

- Prefer `uv sync` for dependency installation.
- Prefer `uv run <command>` when running Python tools in the project environment.
- Keep repeatable local workflows in `Makefile`.
- Keep Makefile target names short and action-oriented.
- Update README commands when Makefile or startup commands change.

## Dependency Rules

- Add runtime packages under `[project].dependencies`.
- Add local tooling under `[dependency-groups].dev`.
- After dependency changes, expect `uv.lock` to change.
- Do not manually edit `uv.lock`; update it through `uv`.

## Lint and Format Rules

- Use Ruff as the formatter and linter.
- Respect the existing line length and quote style.
- Keep Alembic migrations excluded from Ruff unless the migration style is intentionally changed.
- Prefer fixing lint issues in touched code only unless the user asks for a cleanup pass.
- Keep pre-commit hooks aligned with pyproject tooling.

## Test Rules

- Use pytest for tests.
- Async tests should rely on `asyncio_mode = "auto"`.
- Add markers to `[tool.pytest.ini_options]` when introducing integration tests.
- Keep default test runs fast. Mark external-service tests separately.

## Local Infra Rules

- Use `make up` to start local infrastructure and apply migrations.
- Keep queue or bucket provisioning idempotent.
- Use `make down` for teardown.
- Avoid adding local-only setup steps that are not represented in Makefile or README.

## Checklist

- `pyproject.toml`, `uv.lock`, pre-commit, and README agree.
- New commands use `uv run` where appropriate.
- Makefile remains the primary local workflow.
- Tests remain fast by default.
- Integration-test markers are configured when needed.
- Tooling changes do not modify application behavior accidentally.
