---
name: docker-compose-local-infra
description: Mires's Docker Compose local infrastructure pattern for Python FastAPI, Celery, and data services. Use for local Postgres or pgvector, Redis brokers, SQS through LocalStack, MinIO buckets, API and worker services, healthchecks, one-shot provisioning, Makefile wiring, and integration-test infrastructure.
---

# Docker Compose Local Infra

Use this skill when composing local API, worker, Postgres, Redis, SQS or LocalStack, MinIO, or local bootstrap services.

## Source Repo Signals

- Local Compose includes Postgres with pgvector, LocalStack for SQS, MinIO, and a one-shot MinIO bucket creation service: `docker-compose-dev.yml:1`, `docker-compose-dev.yml:2`, `docker-compose-dev.yml:21`, `docker-compose-dev.yml:37`, `docker-compose-dev.yml:60`.
- Compose does not define API, Celery worker, Redis, or Celery beat services. Add them in future repos when local end-to-end behavior should be runnable from one command.
- The Makefile starts Compose, provisions SQS, then applies migrations: `Makefile:12`, `Makefile:15`, `Makefile:16`, `Makefile:17`, `Makefile:36`.
- SQS provisioning is handled by a local script that waits for LocalStack health and creates the queue: `script.py:23`, `script.py:53`, `script.py:65`.
- Worker startup is documented separately instead of composed: `README.md:194`.

## Preferred Compose Shape

For a FastAPI plus Celery repo, prefer one local Compose file with explicit API, worker, database, and broker services:

```yaml
services:
  api:
    build: .
    command: uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      broker:
        condition: service_healthy
    ports:
      - "8000:8000"

  worker:
    build: .
    command: uv run celery -A src.celery_app.app worker --loglevel=INFO
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      broker:
        condition: service_healthy

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  broker:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
```

For SQS or LocalStack instead of Redis, mirror the source repo boundary:

```yaml
services:
  aws:
    image: localstack/localstack
    environment:
      - SERVICES=sqs
      - DEBUG=1
    ports:
      - "4566:4566"
```

Add a one-shot provisioning script or service that waits for LocalStack health and creates queues before workers start.

For S3-compatible local storage, pair the service with a one-shot bucket provisioner. Keep the bucket name in `.env`, wait for MinIO health, and make destructive reset behavior explicit:

```yaml
services:
  minio:
    image: minio/minio
    command: server /data --address 0.0.0.0:9000 --console-address :9001
    environment:
      MINIO_ROOT_USER: miniouser
      MINIO_ROOT_PASSWORD: miniopassword
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  createbucket:
    image: minio/mc
    depends_on:
      minio:
        condition: service_healthy
    environment:
      MINIO_AWS_BUCKET_NAME: ${MINIO_AWS_BUCKET_NAME}
    entrypoint: >
      sh -c "
        mc config host add --quiet --api s3v4 minio http://minio:9000 miniouser miniopassword;
        mc mb --quiet minio/$${MINIO_AWS_BUCKET_NAME} || true;
      "
    restart: "no"

volumes:
  minio_data:
```

## Rules

- Give persistent infrastructure healthchecks and make dependent services wait on health.
- Use `pgvector/pgvector:pg16` when the app stores pgvector embeddings. Source: `docker-compose-dev.yml:4`.
- Keep local service names stable: `db`, `api`, `worker`, `broker`, and optional `aws` or `minio`.
- Use `.env` for local settings, but avoid committing secrets.
- Make `make up` idempotent enough to recreate local infra, provision broker queues or buckets, and apply migrations.
- Keep broker provisioning separate from application startup so API and worker commands stay simple.
- Include API and worker services once local end-to-end runs or integration tests depend on them.

## Anti-Patterns

- Do not leave worker startup only in README once integration tests or full local runs depend on it.
- Do not hardcode SQS queue URLs that depend on generated LocalStack output; derive them from settings or provisioning output.
- Do not reset buckets or queues destructively unless local data loss is intended and clearly scoped. The source MinIO bucket service removes and recreates the bucket: `docker-compose-dev.yml:73`.
- Do not copy SQS-specific `broker_transport_options` into Redis projects.
- Do not start migrations before Postgres is healthy.
