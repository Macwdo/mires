# Private S3/MinIO Upload API

## Purpose and when to use it

Use this module to expose [`storage-s3-core`](storage-s3-core.md)'s
upload/complete/delete lifecycle over DRF endpoints. Requires
`storage-s3-core`.

## When not to use it

Proxy small uploads through Django when simplicity matters more than
web-worker bandwidth — that's a different endpoint shape than this direct
presigned-upload flow, not a reason to skip this module if the core lifecycle
is already selected.

## Responsibilities and invariants

Every endpoint scopes its queryset (via the underlying service calls) to the
requesting account, matching every other tenant-owned resource in this
handbook.

## Complete canonical artifacts

<!-- artifact: src/apps/files/views.py; profiles: storage-django,storage,full -->
```python
from uuid import UUID

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.files.services import complete_upload, delete_file, start_upload


class StartUploadInput(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=127)
    size = serializers.IntegerField(min_value=1)


class StartUploadView(APIView):
    def post(self, request: Request) -> Response:
        serializer = StartUploadInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        grant = start_upload(
            account=request.user.account,
            **serializer.validated_data,
        )
        return Response(
            {
                "file_id": grant.file.pk,
                "upload": {"url": grant.url, "fields": grant.fields},
            },
            status=status.HTTP_201_CREATED,
        )


class CompleteUploadView(APIView):
    def post(self, request: Request, file_id: UUID) -> Response:
        stored_file = complete_upload(
            account=request.user.account,
            file_id=file_id,
        )
        return Response({"id": stored_file.pk, "status": stored_file.status})


class DeleteFileView(APIView):
    def delete(self, request: Request, file_id: UUID) -> Response:
        delete_file(account=request.user.account, file_id=file_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

<!-- artifact: src/apps/files/urls.py; profiles: storage-django,storage,full -->
```python
from django.urls import path

from apps.files.views import CompleteUploadView, DeleteFileView, StartUploadView

app_name = "files"

urlpatterns = [
    path("uploads/", StartUploadView.as_view(), name="upload-start"),
    path(
        "uploads/<uuid:file_id>/complete/",
        CompleteUploadView.as_view(),
        name="upload-complete",
    ),
    path("<uuid:file_id>/", DeleteFileView.as_view(), name="delete"),
]
```

<!-- artifact: src/apps/files/tests/test_views.py; profiles: storage-django,storage,full -->
```python
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User
from apps.files.services import create_download_url


@override_settings(
    AWS_STORAGE_BUCKET_NAME="private-files",
    AWS_S3_ENDPOINT_URL="http://minio:9000",
    AWS_S3_REGION_NAME="us-east-1",
    AWS_ACCESS_KEY_ID="example-access-key",
    AWS_SECRET_ACCESS_KEY="example-secret-key",
)
@patch("apps.files.services.boto3.client")
@pytest.mark.django_db
def test_file_lifecycle_works_through_the_api(
    storage_client_factory: Mock,
    api_client: APIClient,
) -> None:
    # Arrange
    user = User.objects.create_user(email="files@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    api_client.force_authenticate(user=user)
    client = storage_client_factory.return_value
    client.generate_presigned_post.return_value = {
        "url": "http://minio:9000/private-files",
        "fields": {"key": "signed"},
    }
    client.generate_presigned_url.return_value = "http://minio:9000/private-files/download"
    start_url = reverse("files:upload-start")

    # Act
    started = api_client.post(
        start_url,
        {
            "filename": "../../report.pdf",
            "content_type": "application/pdf",
            "size": 128,
        },
    )
    file_id = UUID(started.json()["file_id"])
    client.head_object.return_value = {
        "ContentLength": 128,
        "ContentType": "application/pdf",
        "Metadata": {
            "file-id": str(file_id),
            "account-id": str(account.pk),
        },
    }
    completed = api_client.post(
        reverse("files:upload-complete", kwargs={"file_id": file_id}),
    )
    download_url = create_download_url(
        account=account,
        file_id=file_id,
        client=client,
    )
    deleted = api_client.delete(
        reverse("files:delete", kwargs={"file_id": file_id}),
    )
    deleted_again = api_client.delete(
        reverse("files:delete", kwargs={"file_id": file_id}),
    )

    # Assert
    assert started.status_code == status.HTTP_201_CREATED
    assert started.json()["upload"]["url"] == "http://minio:9000/private-files"
    assert completed.status_code == status.HTTP_200_OK
    assert completed.json() == {"id": str(file_id), "status": "ready"}
    assert download_url == "http://minio:9000/private-files/download"
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert deleted_again.status_code == status.HTTP_204_NO_CONTENT
    client.delete_object.assert_called_once()
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: storage-django -->
```toml
  "django-storages[s3]==1.14.6",
```

## Alternatives and trade-offs

See [storage-s3-core](storage-s3-core.md) for the upload-transport
trade-offs; this module only adds the HTTP surface.

## Required tests

Cover the full API lifecycle (start, complete, download, idempotent
delete) with a mocked S3 client; boundary and integration cases live in
[storage-s3-core](storage-s3-core.md).

## Related standards

See [storage-s3-core](storage-s3-core.md), [API design](../../docs/api-design.md),
and [security](../../docs/security.md).
