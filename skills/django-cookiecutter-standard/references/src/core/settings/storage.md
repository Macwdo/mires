# Object Storage Settings

## Purpose and when to use it

Use this module for the S3-compatible credentials and limits consumed by
[storage](../../../recipes/storage/storage-django.md).

## When not to use it

Do not read these values directly in application code; go through the
storage backend so a swapped provider only changes this module.

## Responsibilities and invariants

A separate public endpoint is supported for setups where the
application-facing S3 endpoint (e.g. an internal MinIO host) differs from
the one used to build public URLs; it falls back to the private endpoint
when unset.

## Complete canonical artifact

<!-- artifact: src/core/settings/storage.py; profiles: base -->
```python
from decouple import config

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default=None) or None
AWS_S3_PUBLIC_ENDPOINT_URL = (
    config("AWS_S3_PUBLIC_ENDPOINT_URL", default=None) or AWS_S3_ENDPOINT_URL
)
AWS_PRESIGNED_EXPIRY_SECONDS = config("AWS_PRESIGNED_EXPIRY_SECONDS", default=300, cast=int)
MAX_UPLOAD_BYTES = config("MAX_UPLOAD_BYTES", default=10485760, cast=int)
```

## Required tests

Settings import with credentials unset; a presigned URL uses
`AWS_S3_PUBLIC_ENDPOINT_URL` when it differs from `AWS_S3_ENDPOINT_URL`.

## Related standards

See [base](base.md) and [storage](../../../recipes/storage/storage-django.md).
