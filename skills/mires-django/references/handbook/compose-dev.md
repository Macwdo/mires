# Local Infrastructure Compose

## Purpose and when to use it

This development artifact runs PostgreSQL with pgvector, Redis, and private MinIO while Django runs on the host.

## Complete canonical artifact

<!-- artifact: compose.dev.yaml; profiles: full -->
```yaml
name: django-standard-dev
services:
  postgres:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_DB: django_standard
      POSTGRES_USER: django_standard
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U django_standard -d django_standard"]
      interval: 5s
      timeout: 3s
      retries: 20

  redis:
    image: redis:8.4-alpine
    command: ["redis-server", "--appendonly", "yes"]
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 20

  minio:
    image: minio/minio:RELEASE.2025-09-07T16-13-09Z
    command: ["server", "/data", "--console-address", ":9001"]
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:?set MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:?set MINIO_ROOT_PASSWORD}
    ports:
      - "127.0.0.1:9000:9000"
      - "127.0.0.1:9001:9001"
    volumes:
      - minio-data:/data

volumes:
  postgres-data:
  redis-data:
  minio-data:
```

## Responsibilities and invariants

Infrastructure ports bind only to loopback and credentials are required from the caller.

## Required tests

Run `docker compose -f compose.dev.yaml config` and wait for health checks before integration tests.
