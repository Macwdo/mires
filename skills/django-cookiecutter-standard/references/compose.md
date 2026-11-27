# Full-Profile Compose

## Purpose and when to use it

This artifact is an integration environment for the reconstructed full profile, not a production orchestrator.

## Complete canonical artifact

<!-- artifact: compose.yaml; profiles: base -->
```yaml
name: django-standard-base
services:
  web:
    build: .
    command: ["gunicorn", "--chdir", "/app/src", "--config", "/app/gunicorn.conf.py", "core.wsgi:application"]
    environment:
      ENVIRONMENT: local
      DATABASE_URL: postgresql://django_standard:${POSTGRES_PASSWORD:-replace-local-password}@postgres:5432/django_standard
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: django_standard
      POSTGRES_USER: django_standard
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-replace-local-password}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U django_standard -d django_standard"]
      interval: 5s
      timeout: 3s
      retries: 20

volumes:
  postgres-data:
```

<!-- artifact: compose.yaml; profiles: full -->
```yaml
name: django-standard
services:
  web:
    build: .
    command: ["gunicorn", "--chdir", "/app/src", "--config", "/app/gunicorn.conf.py", "core.wsgi:application"]
    environment:
      ENVIRONMENT: local
      DATABASE_URL: postgresql://django_standard:${POSTGRES_PASSWORD:-replace-local-password}@postgres:5432/django_standard
      CELERY_BROKER_URL: redis://redis:6379/0
      REDIS_URL: redis://redis:6379/1
      AWS_S3_ENDPOINT_URL: http://minio:9000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  worker:
    build: .
    command: ["celery", "--workdir", "/app/src", "-A", "core.celery:app", "worker", "--loglevel=INFO"]
    environment:
      ENVIRONMENT: local
      DATABASE_URL: postgresql://django_standard:${POSTGRES_PASSWORD:-replace-local-password}@postgres:5432/django_standard
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  beat:
    build: .
    command: ["celery", "--workdir", "/app/src", "-A", "core.celery:app", "beat", "--loglevel=INFO", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
    environment:
      ENVIRONMENT: local
      DATABASE_URL: postgresql://django_standard:${POSTGRES_PASSWORD:-replace-local-password}@postgres:5432/django_standard
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_DB: django_standard
      POSTGRES_USER: django_standard
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-replace-local-password}
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
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-local-access-key}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-replace-local-secret}
    volumes:
      - minio-data:/data

volumes:
  postgres-data:
  redis-data:
  minio-data:
```

## Responsibilities and invariants

Compose is for integration and demonstrations. Production uses managed secrets, durable services, TLS, backups, and an orchestrator.

## Required tests

Run `docker compose config`, bring dependencies healthy, migrate once, and execute the integration suite.
