# Private S3/MinIO Upload Core

## Purpose and when to use it

Use this module for private user files that should travel directly between
the client and an S3-compatible object store. It owns the `StoredFile`
record and the boto3-based presign/verify/delete lifecycle, independent of
how that lifecycle is exposed over HTTP (see [`storage-django`](storage-django.md)
for the DRF views).

## When not to use it

Do not use public buckets for private objects, trust a browser's reported
MIME type, accept a client-selected object key, or treat a successful
presign response as proof that an upload completed.

## Responsibilities and invariants

- Object keys are server-generated, unpredictable, and account-prefixed.
- `start_upload` enforces an allowlist and maximum size.
- The signed POST enforces the same size and MIME constraints.
- `complete_upload` verifies object existence, exact size, content type, and
  ownership.
- Download and deletion always scope the database lookup to the account.
- Object deletion is idempotent and the row records deletion time.

## Complete canonical artifacts

<!-- artifact: src/apps/files/apps.py; profiles: storage-s3-core,storage,full -->
```python
from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.files"
```

<!-- artifact: src/apps/files/models.py; profiles: storage-s3-core,storage,full -->
```python
from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models

from apps.account.models import AccountOwnedModel


class StoredFile(AccountOwnedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_key = models.CharField(max_length=512, unique=True)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127)
    expected_size = models.PositiveBigIntegerField()
    status = models.CharField(max_length=16, choices=Status, default=Status.PENDING)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects: models.Manager[StoredFile] = models.Manager()

    class Meta:
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "status", "-created_at"),
                name="file_account_status_idx",
            )
        ]
```

<!-- artifact: src/apps/files/services.py; profiles: storage-s3-core,storage,full -->
```python
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

import boto3
from botocore.client import BaseClient
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.account.models import Account
from apps.files.models import StoredFile

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
}


@dataclass(frozen=True, slots=True)
class UploadGrant:
    file: StoredFile
    url: str
    fields: dict[str, str]


def storage_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _safe_suffix(filename: str) -> str:
    suffix = PurePath(filename).suffix.lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{1,10}", suffix) else ""


@transaction.atomic
def start_upload(
    *,
    account: Account,
    filename: str,
    content_type: str,
    size: int,
    client: BaseClient | None = None,
) -> UploadGrant:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError({"content_type": "This file type is not allowed."})
    if size <= 0 or size > MAX_UPLOAD_BYTES:
        raise ValidationError(
            {"size": f"File size must be between 1 and {MAX_UPLOAD_BYTES} bytes."}
        )

    file_id = uuid.uuid4()
    object_key = f"accounts/{account.pk}/files/{file_id}{_safe_suffix(filename)}"
    stored_file = StoredFile.objects.create(
        id=file_id,
        account=account,
        object_key=object_key,
        original_name=PurePath(filename).name[:255],
        content_type=content_type,
        expected_size=size,
    )
    s3 = client or storage_client()
    post: dict[str, Any] = s3.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=object_key,
        Fields={
            "Content-Type": content_type,
            "x-amz-meta-file-id": str(file_id),
            "x-amz-meta-account-id": str(account.pk),
        },
        Conditions=[
            {"Content-Type": content_type},
            {"x-amz-meta-file-id": str(file_id)},
            {"x-amz-meta-account-id": str(account.pk)},
            ["content-length-range", size, size],
        ],
        ExpiresIn=600,
    )
    return UploadGrant(
        file=stored_file,
        url=str(post["url"]),
        fields={str(key): str(value) for key, value in post["fields"].items()},
    )


@transaction.atomic
def complete_upload(
    *,
    account: Account,
    file_id: uuid.UUID,
    client: BaseClient | None = None,
) -> StoredFile:
    stored_file = StoredFile.objects.select_for_update().get(
        pk=file_id,
        account=account,
        status=StoredFile.Status.PENDING,
    )
    s3 = client or storage_client()
    metadata = s3.head_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=stored_file.object_key,
    )
    if metadata["ContentLength"] != stored_file.expected_size:
        raise ValidationError({"file": "Uploaded size does not match the request."})
    if metadata["ContentType"] != stored_file.content_type:
        raise ValidationError({"file": "Uploaded content type does not match."})
    object_metadata = metadata.get("Metadata", {})
    if object_metadata.get("file-id") != str(stored_file.pk):
        raise ValidationError({"file": "Object metadata does not match the file."})
    if object_metadata.get("account-id") != str(account.pk):
        raise ValidationError({"file": "Object metadata does not match the account."})

    stored_file.status = StoredFile.Status.READY
    stored_file.save(update_fields=("status", "updated_at"))
    return stored_file


def create_download_url(
    *,
    account: Account,
    file_id: uuid.UUID,
    client: BaseClient | None = None,
) -> str:
    stored_file = StoredFile.objects.get(
        pk=file_id,
        account=account,
        status=StoredFile.Status.READY,
    )
    s3 = client or storage_client()
    return str(
        s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": stored_file.object_key,
                "ResponseContentDisposition": (
                    f'attachment; filename="{stored_file.original_name}"'
                ),
            },
            ExpiresIn=300,
        )
    )


@transaction.atomic
def delete_file(
    *,
    account: Account,
    file_id: uuid.UUID,
    client: BaseClient | None = None,
) -> StoredFile:
    stored_file = StoredFile.objects.select_for_update().get(
        pk=file_id,
        account=account,
    )
    if stored_file.status == StoredFile.Status.DELETED:
        return stored_file
    s3 = client or storage_client()
    s3.delete_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=stored_file.object_key,
    )
    stored_file.status = StoredFile.Status.DELETED
    stored_file.deleted_at = timezone.now()
    stored_file.save(update_fields=("status", "deleted_at", "updated_at"))
    return stored_file
```

<!-- artifact: src/apps/files/tests/test_services.py; profiles: storage-s3-core,storage,full -->
```python
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from apps.account.models import Account
from apps.authentication.models import User
from apps.files.services import start_upload


@pytest.mark.django_db
def test_disallowed_content_type_is_rejected() -> None:
    # Arrange
    user = User.objects.create_user(email="files@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    client = Mock()

    # Assert
    with pytest.raises(ValidationError):
        start_upload(
            account=account,
            filename="program.bin",
            content_type="application/octet-stream",
            size=128,
            client=client,
        )
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: storage-s3-core -->
```toml
  "boto3==1.43.56",
  "botocore==1.43.56",
```

<!-- dependency-fragment: pyproject.toml#dev; modules: storage-s3-core -->
```toml
  "moto[s3]==5.2.2",
```

## Alternatives and trade-offs

Presigned POST supports enforceable conditions and browser form uploads.
Presigned PUT has a simpler client shape but fewer policy conditions.
Multipart uploads are appropriate for very large objects and require durable
part state and abort cleanup. Malware scanning can move a verified object
from quarantine to a ready prefix before exposing download URLs.

## Required tests

Use MinIO for integration tests. Cover exact boundary sizes, spoofed MIME
and metadata, missing objects, foreign-account identifiers, expired
signatures, path-like filenames, duplicate completion and deletion, private
bucket policy, download expiry, and cleanup of abandoned pending rows.

## Related standards

See [storage-django](storage-django.md), [security](../../docs/security.md),
and [operations](../../docs/operations.md).
