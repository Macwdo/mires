---
name: macwdo-python-docker-compose-patterns
description: Macwdo's Docker Compose patterns for Python service repos. Use for docker-compose-dev.yml, Postgres pgvector, LocalStack SQS, MinIO, one-shot provisioning services, healthchecks, persistent volumes, port mappings, Makefile wiring, and local API or Celery worker service additions.
---

# Docker Compose Patterns

Use this skill when changing local Compose services or the Makefile workflow around local infrastructure.

For deeper local infrastructure examples, use `macwdo-python-docker-compose-local-infra`.

## Source Repo Signals

- Local Compose is in `docker-compose-dev.yml`: `docker-compose-dev.yml:1`.
- Postgres runs with pgvector support: `docker-compose-dev.yml:2`, `docker-compose-dev.yml:4`.
- Postgres has a readiness healthcheck and persistent volume: `docker-compose-dev.yml:10`, `docker-compose-dev.yml:16`.
- LocalStack is used for SQS: `docker-compose-dev.yml:21`, `docker-compose-dev.yml:28`.
- MinIO is used for S3-compatible object storage and has a healthcheck: `docker-compose-dev.yml:37`, `docker-compose-dev.yml:49`.
- Bucket creation is a one-shot Compose service depending on healthy MinIO: `docker-compose-dev.yml:60`, `docker-compose-dev.yml:63`, `docker-compose-dev.yml:70`.
- `make up` starts Compose, provisions LocalStack/SQS, then applies migrations: `Makefile:12`, `Makefile:15`, `Makefile:16`, `Makefile:17`.
- `make down` removes the local Compose stack: `Makefile:26`, `Makefile:28`.
- LocalStack queue provisioning waits for service health in `script.py`: `script.py:23`, `script.py:53`, `script.py:65`.

## Compose Rules

- Keep local-only infrastructure in `docker-compose-dev.yml`.
- Prefer explicit service names: `db`, `aws`, `minio`, and one-shot provisioning service names.
- Use `depends_on` with `condition: service_healthy` for services that truly require readiness.
- Add healthchecks for services that other services depend on.
- Use named volumes for stateful services.
- Keep ports explicit and predictable for local tools.
- Use `.env` interpolation for application-specific values such as bucket and queue names.
- Do not bake real credentials into Compose. Local demo credentials are acceptable only for local-only services.

## One-Shot Provisioning Rules

- Use one-shot services for idempotent setup like bucket creation.
- Set `restart: "no"` on one-shot services.
- Make setup commands idempotent with `|| true` only where deleting/recreating local resources is intentional.
- Keep more complex provisioning in a small script when health polling or SDK calls are easier than shell.

## Makefile Rules

- Keep `make up` as the end-to-end local bootstrap: Compose up, queue/bootstrap scripts, migrations.
- Keep `make down` as the matching teardown.
- Keep Alembic commands in Makefile targets so users do not need to remember raw CLI flags.
- Use `uv run` for Python scripts that depend on the project environment.

## Adding API or Worker Services

When local end-to-end execution should be one command, add API and worker services to Compose:

- API command: `uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000`.
- Worker command: `uv run celery -A src.celery_app.app worker --loglevel=INFO`.
- Both should read `.env`.
- Both should depend on database and broker readiness.
- The worker should not expose ports unless needed for diagnostics.

## Checklist

- New service has a clear local purpose.
- Stateful service has a named volume.
- Dependent services wait for health, not just container start.
- Makefile remains the primary local workflow.
- LocalStack and MinIO setup stays idempotent.
- No production credentials or URLs are introduced.
