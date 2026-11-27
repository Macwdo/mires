# Environment Variables

## Purpose and when to use it

Copy the reconstructed `.env.example` to an untracked local file and replace placeholders. Production secrets belong in a secret manager.

## When not to use it

Never commit a populated environment file or reuse local example credentials in a public deployment.

## Responsibilities and invariants

The artifact contains placeholders and private local defaults only. Optional recipe variables are documented together so profile upgrades do not require discovering hidden settings.

## Complete canonical artifact

<!-- artifact: .env.example; profiles: base -->
```dotenv
ENVIRONMENT=local
DEBUG=false
SECRET_KEY=replace-with-at-least-50-random-characters-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
DATABASE_URL=postgresql://postgres:replace-local-password@localhost:5432/django_standard
LOG_LEVEL=INFO
# {{FRAGMENT:env}}

API_THROTTLE_ANON=100/hour
API_THROTTLE_USER=2000/day
API_THROTTLE_BURST=60/minute
API_THROTTLE_REGISTRATION=5/hour
API_THROTTLE_TOKEN=10/minute
API_THROTTLE_TOKEN_REFRESH=30/minute
API_THROTTLE_TOKEN_VERIFY=60/minute
API_THROTTLE_CUSTOMERS=600/hour

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=django-db
REDIS_URL=redis://localhost:6379/1

AWS_ACCESS_KEY_ID=local-access-key
AWS_SECRET_ACCESS_KEY=replace-local-secret
AWS_STORAGE_BUCKET_NAME=private-files
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=http://localhost:9000
AWS_S3_PUBLIC_ENDPOINT_URL=http://localhost:9000
AWS_PRESIGNED_EXPIRY_SECONDS=300
MAX_UPLOAD_BYTES=10485760

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-sol
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
OPENAI_SAFETY_IDENTIFIER_SECRET=replace-with-a-separate-random-secret

DEFAULT_FROM_EMAIL=no-reply@localhost
```

## Alternatives and trade-offs

`python-decouple` (see [settings](src/core/settings/README.md)) reads and casts every variable in one call, so this reference has no hand-rolled parsing helpers to keep in sync.

## Required tests

Secret-scan the repository and test every production-required variable.

## Related standards

See [settings](src/core/settings/README.md) and [security](docs/security.md).
