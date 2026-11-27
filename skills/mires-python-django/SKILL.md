---
name: mires-python-django
description: Apply Macwdo's typed Django and Django REST Framework standards for uv, Ruff, ty, models, migrations, selectors, services, serializers, endpoints, nested routers, authentication, testing, and operations. Includes the complete Django backend standard handbook (architecture, conventions, API design, security, testing, operations, and recipes). Use only when Django or DRF owns the application boundary.
---

# Mires Python Django

Use this skill with `$mires-python` for Django and DRF work. Inspect the target project before applying a pattern; preserve its settings layout, app boundaries, model base classes, API conventions, test helpers, and operational choices.

## Snippet-Driven Implementation

Always start Django code generation from the closest snippet in this `SKILL.md`: model, migration, selector, service, serializer, APIView, ViewSet, nested router, route, task, or test. Also consult `$mires-python` for shared Python, Celery, database, and typing shapes.

- Preserve the snippet's separation of reads, writes, validation, response shaping, transactions, and effects.
- Adapt base classes, module locations, authentication, permissions, exception types, fixtures, and naming to the target project.
- Never copy example app names, URLs, model fields, or account assumptions unchanged.
- When nearby Django code conflicts with a snippet, follow the repository and retain only the compatible invariant.
- Generate the focused test from the corresponding test snippet as part of the implementation when behavior changes.

## Django Tooling And Typing: uv, Ruff, And ty

Django projects inherit the complete `$mires-python` toolchain contract:

- Use `uv` for Python versions, environments, dependency groups, lockfiles, and every project command.
- Use Ruff for formatting and linting, including Django-specific lint rules when they fit the project.
- Use `ty` as the only static type checker.
- Use pytest and pytest-django for tests unless the repository already standardizes on Django's test runner.

### Django Project Bootstrap

```bash
uv init
uv python pin 3.12
uv add django djangorestframework drf-nested-routers pydantic
uv add --dev pytest pytest-django ruff ty
uv sync
```

Type stub packages are optional aids, not the type checker:

```bash
uv add --dev django-stubs djangorestframework-stubs
```

`ty` reads installed `.pyi` stub packages but does not execute mypy plugins. Do not add `mypy_django_plugin`, `mypy_drf_plugin`, or `[tool.mypy]` configuration to a `ty` project. Trial the stubs against the installed Django/DRF versions and keep them only when they improve diagnostics without depending on plugin-generated behavior.

### Django pyproject.toml Reference

```toml
[project]
requires-python = ">=3.12"
dependencies = [
  "django",
  "djangorestframework",
  "drf-nested-routers",
  "pydantic",
]

[dependency-groups]
dev = [
  "pytest",
  "pytest-django",
  "ruff",
  "ty",
]

[tool.ruff]
target-version = "py312"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF", "DJ"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true

[tool.ty.src]
include = ["src", "tests", "manage.py"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests"]
```

Adjust the source root and settings module to the repository. `ty` derives its Python target from `project.requires-python`; configure `[tool.ty.environment]` only for a nonstandard source layout or interpreter.

### What To Type In A Django Project

- Model methods, properties, custom fields, managers, and QuerySet methods.
- Selector inputs and `QuerySet[Model]` return values.
- Service inputs, DTOs, domain exceptions, and model return values.
- Serializer `create()`, `update()`, `validate()`, and custom field methods.
- View/ViewSet `get_queryset()`, `get_serializer_class()`, actions, and helper methods.
- Celery task payloads and return values.
- Settings helpers, storage adapters, SDK clients, signals, and management commands.
- Test fixtures and reusable factories when inference is unclear.

Do not annotate every Django model field redundantly when the assignment is already clear. Concentrate annotations at public boundaries and dynamic framework extension points. Do not annotate dictionaries or mappings with an unconstrained value type; those annotations add no information.

Use a `TypedDict` when a value stays a dictionary and its keys are known. Do not invent a Pydantic DTO that only restates `validated_data`.

Name type variables without a leading underscore, for example `ModelT`.

### Django DTOs And Typed Dicts

- Keep request validation in DRF serializers.
- When the serializer write shape already matches the service or model fields, call the service with `**serializer.validated_data` or, inside `create()`, `**validated_data`.
- When the caller already has a Pydantic DTO, expand it with `**data.model_dump()`.
- Introduce a Pydantic DTO when the service is called without a serializer, when the input shape differs from the serializer, or when the payload must carry an already-resolved Django model.
- Use `TypedDict` for dictionary contracts that remain dictionaries: serializer context, JSON-like test payloads, and other fixed key sets.

Enable `arbitrary_types_allowed` only when a DTO must hold a non-Pydantic object such as a Django model instance. Primitive serializer fields do not need a DTO.

```python
from pydantic import BaseModel, ConfigDict

from .models import BillingProfile, Invoice


class InvoiceCreateDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    reference: str
    customer_profile: BillingProfile


def invoice_create(*, owner, data: InvoiceCreateDTO) -> Invoice:
    return Invoice.objects.create(owner=owner, **data.model_dump())
```

Use that DTO after a related object has already been resolved. Do not wrap a one-field serializer payload in a matching one-field DTO.

### Typed QuerySet, Selector, And Service

```python
from __future__ import annotations

from typing import Self

from django.contrib.auth.models import AbstractBaseUser
from django.db import models, transaction
from django.db.models import QuerySet


class CustomerQuerySet(models.QuerySet):
    def active(self) -> Self:
        return self.filter(is_active=True)


class CustomerManager(models.Manager):
    def get_queryset(self) -> CustomerQuerySet:
        return CustomerQuerySet(self.model, using=self._db)

    def active(self) -> CustomerQuerySet:
        return self.get_queryset().active()


class Customer(models.Model):
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="customers",
    )
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    objects = CustomerManager()

    def __str__(self) -> str:
        return self.name


def customer_list(*, owner: AbstractBaseUser) -> QuerySet[Customer]:
    return Customer.objects.active().filter(owner=owner)


@transaction.atomic
def customer_create(*, owner: AbstractBaseUser, name: str) -> Customer:
    return Customer.objects.create(owner=owner, name=name)
```

Use the repository's concrete user model type when available. Pass model instances as method arguments. When the caller is a serializer, spread `**validated_data` into those arguments instead of building a DTO.

### Typed DRF Boundary

```python
from django.db.models import QuerySet
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def create(self, validated_data) -> Customer:
        request = self.context["request"]
        return customer_create(owner=request.user, **validated_data)


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerCreateSerializer

    def get_queryset(self) -> QuerySet[Customer]:
        return customer_list(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def deactivate(self, request: Request, pk: str | None = None) -> Response:
        customer: Customer = self.get_object()
        customer.is_active = False
        customer.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
```

Leave DRF `validated_data` untyped. Spread it into the service when the keys already match. Build a Pydantic DTO only when the service input is a different shape or must carry a resolved model.

Some stub packages describe `ModelSerializer` or `GenericViewSet` as generic even when the runtime class is not subscriptable. Do not write `ModelSerializer[Customer]` or `GenericViewSet[Customer]` unless the installed runtime explicitly supports that syntax or the project intentionally applies a compatible runtime patch.

### Required Django Validation

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

Run migration checks when models or migration state may have changed. Add `manage.py check --deploy` in a production configuration validation path, not as a substitute for normal tests.

## Boundaries

- Keep framework wiring thin and domain behavior explicit.
- Use services for transactional writes or effects when the repository uses that boundary.
- Use selectors for reusable or complex reads when the repository uses them.
- Do not add repository or use-case layers merely to imitate another architecture.
- Keep account and tenant scoping in the query before object lookup or mutation.
- Validate with the project's Django and DRF tests, migrations, and system checks.

For non-Django Python, use `$mires-python`. For LangChain integrations hosted inside Django, apply `$mires-python-langchain` as an additional skill without replacing Django's lifecycle and persistence conventions.

## Settings And Startup

- Follow the project's existing settings split, environment loader, and deployment overrides.
- Keep secrets environment-backed and validate required production settings at startup or deployment checks.
- Avoid importing models, opening connections, or starting network clients in settings modules.
- Use `AppConfig.ready()` only for registration work that Django requires; keep it idempotent under autoreload and tests.
- Preserve WSGI and ASGI entrypoints and choose async only when the full call path supports it.

## Authentication, Authorization, And Tenancy

- Use the project's established authentication classes and permission model.
- Scope tenant- or account-owned querysets before lookup, update, or delete.
- Do not fetch globally and check ownership afterward when the scoped query can enforce it.
- Keep object permissions and role checks explicit at the API or service boundary.
- Return consistent not-found or forbidden behavior without leaking object existence.
- Test anonymous, authenticated, wrong-tenant, wrong-role, and allowed paths.

## API Cross-Cutting Rules

- Keep request validation in input serializers and response shaping in output serializers.
- Translate domain failures through the project's exception handler or established API error format.
- Reuse pagination, filter backends, ordering, throttling, and schema conventions already present.
- Avoid hidden writes in serializer representation or selector code.
- Optimize list and detail querysets for the serializers they feed.
- Version or coordinate externally consumed contract changes with their clients.

## Files, Storage, And External Effects

- Validate file size, content type, extension, and ownership; treat filenames and metadata as untrusted.
- Store durable object identifiers rather than expiring download URLs.
- Keep storage and SDK clients behind explicit adapters or injected service dependencies.
- Dispatch irreversible effects after a successful transaction using the project's established pattern.
- Make retries idempotent with stable operation keys or durable status rows.

### Direct S3 Upload Start And Confirm

Use this connected reference when the browser uploads directly to S3-compatible storage and confirmation only records that the client completed the upload. Adapt model fields, account ownership, settings, and route names to the repository. The persisted `File` row owns the server-generated object key, declared content type and size, and confirmation timestamp.

The start service creates a pending record and returns a constrained presigned POST. The confirm service only marks that record as finished; it does not call object storage:

```python
from __future__ import annotations

from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from django.utils import timezone
from mypy_boto3_s3 import S3Client

from apps.account.models import Account
from apps.common.services.storage import (
    PresignedPost,
    generate_upload_presigned_post,
)
from apps.storage.models import File


class FileUploadStartResult(TypedDict):
    file: File
    upload: PresignedPost


def file_upload_start(
    *,
    account: Account,
    filename: str,
    content_type: str,
    expected_size: int,
    bucket_name: str,
    expires_in: int,
    s3_client: S3Client,
) -> FileUploadStartResult:
    original_name = Path(filename).name
    suffix = Path(original_name).suffix.lower()
    object_key = f"files/{account.pk}/{uuid4().hex}{suffix}"

    upload = generate_upload_presigned_post(
        bucket_name=bucket_name,
        object_key=object_key,
        content_type=content_type,
        expected_size=expected_size,
        expires_in=expires_in,
        s3_client=s3_client,
    )

    file = File(
        owned_by=account,
        name=original_name,
        path=object_key,
        type=content_type,
        size=expected_size,
        upload_finished_at=None,
    )
    file.full_clean()
    file.save()
    return FileUploadStartResult(file=file, upload=upload)


def file_upload_confirm(
    *,
    file: File,
) -> File:
    if file.upload_finished_at is not None:
        return file

    file.upload_finished_at = timezone.now()
    file.full_clean()
    file.save(update_fields=["upload_finished_at", "updated_at"])
    return file
```

Use dedicated serializers for the start request, response, and confirmation. The confirmation endpoint receives `file_id`, resolves it through the account-scoped queryset, and updates the database:

```python
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.dependencies import get_application_default_s3
from apps.storage.models import File
from apps.storage.services import file_upload_confirm, file_upload_start


class FileUploadStartSerializer(serializers.Serializer):
    filename = serializers.CharField(allow_blank=False)
    content_type = serializers.CharField(allow_blank=False)
    size = serializers.IntegerField(min_value=1)


class PresignedPostSerializer(serializers.Serializer):
    url = serializers.URLField()
    fields = serializers.DictField(child=serializers.CharField())


class FileUploadStartResponseSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    upload = PresignedPostSerializer()


class FileUploadConfirmSerializer(serializers.Serializer):
    file_id = serializers.IntegerField(min_value=1)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "type", "size", "upload_finished_at"]
        read_only_fields = fields


class FileViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileSerializer

    def get_queryset(self) -> QuerySet[File]:
        return File.objects.filter(owned_by=self.request.user.current_account)

    @action(detail=False, methods=["post"], url_path="upload-start")
    def upload_start(self, request: Request) -> Response:
        input_serializer = FileUploadStartSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        bucket_name, s3_client = get_application_default_s3()
        result = file_upload_start(
            account=request.user.current_account,
            filename=input_serializer.validated_data["filename"],
            content_type=input_serializer.validated_data["content_type"],
            expected_size=input_serializer.validated_data["size"],
            bucket_name=bucket_name,
            expires_in=settings.AWS_PRESIGNED_EXPIRE,
            s3_client=s3_client,
        )
        output = FileUploadStartResponseSerializer({
            "file_id": result["file"].pk,
            "upload": result["upload"],
        })
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="confirm-upload")
    def confirm_upload(self, request: Request) -> Response:
        input_serializer = FileUploadConfirmSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        file = get_object_or_404(
            self.get_queryset(),
            pk=input_serializer.validated_data["file_id"],
        )
        confirmed = file_upload_confirm(file=file)
        return Response(FileSerializer(confirmed).data, status=status.HTTP_200_OK)
```

The serializer above shows the wire shape. Add the repository's size ceiling and content-type and extension allowlists before using those values to sign a POST. Test that confirmation persists the timestamp and remains scoped to the current account:

```python
import pytest

from apps.storage.models import File
from apps.storage.services import file_upload_confirm


@pytest.mark.django_db
def test_file_upload_confirm_persists_timestamp(account) -> None:
    file = File.objects.create(
        owned_by=account,
        name="contract.pdf",
        path="files/1/example.pdf",
        type="application/pdf",
        size=128,
    )

    confirmed = file_upload_confirm(file=file)
    repeated = file_upload_confirm(file=confirmed)

    confirmed.refresh_from_db()
    assert confirmed.upload_finished_at is not None
    assert repeated.pk == confirmed.pk
```

Also cover authentication, another account, an unknown `file_id`, repeated confirmation, and invalid start metadata through DRF endpoint tests. This contract deliberately treats the authenticated confirmation call as the completion signal and does not verify the object in storage.

## Celery And Background Work

- Keep tasks thin: accept scalar identifiers, create worker-local resources, call a service, and persist status.
- Never pass model instances, request objects, open files, sessions, or secrets in task payloads.
- Use `transaction.on_commit()` when enqueueing depends on newly committed data.
- Define retryable versus permanent failures and bound retries.
- Test services and task wrappers separately; add a live-worker test only for broker/worker integration risk.
- Apply `$mires-python` for the shared Celery, Postgres, settings, and test rules.

## Realtime And Async

- Keep WebSocket authorization and tenant scoping equivalent to HTTP access rules.
- Use channel groups or subscriptions with stable, non-secret names.
- Do not hold database transactions open while streaming or waiting on network I/O.
- Separate event production from transport so domain behavior remains testable.
- Define reconnect, ordering, duplicate, and missed-event behavior when realtime delivery matters.

## Operations

- Provide health checks that distinguish process liveness from dependency readiness where the deployment needs both.
- Run migrations as an explicit release step rather than on every web worker startup.
- Keep static/media serving ownership clear between Django, object storage, and the reverse proxy.
- Configure trusted hosts, proxy SSL headers, secure cookies, CSRF origins, CORS, and logging for the public deployment topology.
- Verify `manage.py check --deploy` or the repository's equivalent production checks.

## Test Matrix

- Models: constraints, defaults, derived behavior, and migration compatibility.
- Selectors: scoping, filtering, ordering, annotations, and query count where material.
- Services: transactions, idempotency, effects, domain failures, and retries.
- Serializers: valid/invalid inputs and stable output contracts.
- APIs: authentication, authorization, status, body, pagination, and error shape. Arrange through `given_*` HTTP helpers and assert with Given / When / Then.
- Operations: settings validation, health endpoints, task wiring, and storage adapters when changed.

## Simple Relational CRUD: ModelSerializer And ModelViewSet Reference

Use this connected example as the primary snippet only when generating simple, resource-shaped relational CRUD with DRF. Adapt names, base models, ownership, permissions, filters, error shape, and test helpers to the repository.

This is not the default for workflows with approvals, cross-aggregate invariants, external effects, complex transactions, state machines, or action-specific permissions. Put those behaviors in services and expose them through explicit APIViews or `@action` endpoints instead of stretching `ModelViewSet` and `ModelSerializer` beyond mechanical CRUD.

### Relationship Decision Rules

- One-to-One (OtO): use `OneToOneField` when each parent owns at most one related row, such as `Customer.profile`.
- One-to-Many (OtM): place a `ForeignKey` on the child when one parent owns many children, such as `Customer.addresses`.
- Forward `ForeignKey` and One-to-One reads use `select_related()`.
- Reverse One-to-Many and Many-to-Many reads use `prefetch_related()`.
- Nested read serializers are straightforward; use `many=True` for to-many fields and `read_only=True` when writes happen on nested-router child endpoints.
- DRF does not implement writable nested `ModelSerializer` persistence automatically. Use an explicit transactional `create()` only for one-request aggregate creates. Give related-resource list, create, update, and delete to a `NestedSimpleRouter` child ViewSet.
- Register a nested router when the child does not exist without its parent, such as `Customer.addresses` or `Customer.profile`. Keep a top-level router when clients look the child up independently.
- Prefer explicit nested fields over `Meta.depth`; explicit serializers make the API contract, query requirements, and write behavior visible.
- Use different read/create/update serializers when the wire shapes or responsibilities differ.

### Models: OtO And OtM

```python
from __future__ import annotations

from django.conf import settings
from django.db import models


class Customer(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customers",
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class CustomerProfile(models.Model):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)


class Address(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(max_length=50)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=2)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "label", "id"]
```

Use `PROTECT` instead of `CASCADE` when deletion must be refused while children exist. Use `SET_NULL` only when a nullable orphan has valid domain meaning.

### ModelSerializers For Nested Reads

```python
from rest_framework import serializers

from .models import Address, Customer, CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["id", "phone", "notes"]
        read_only_fields = ["id"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "label", "city", "country", "is_primary"]
        read_only_fields = ["id"]


class CustomerReadSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "email",
            "profile",
            "addresses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
```

The field names match `related_name`, so no `source=` is needed. If the API name differs from the model relation, declare `source` explicitly.

### Writable Nested Create

Use explicit transactional persistence when one request intentionally creates the aggregate:

```python
from django.db import transaction
from rest_framework import serializers

from .models import Address, Customer, CustomerProfile


class CustomerCreateSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer()
    addresses = AddressSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = ["id", "name", "email", "profile", "addresses"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data) -> Customer:
        profile_data = validated_data.pop("profile")
        addresses_data = validated_data.pop("addresses", [])

        customer = Customer.objects.create(**validated_data)
        CustomerProfile.objects.create(customer=customer, **profile_data)

        for address_data in addresses_data:
            Address.objects.create(customer=customer, **address_data)

        return customer
```

`serializer.save(owner=request.user)` adds `owner` to `validated_data` before `create()` runs. If the repository puts multi-model writes in services, keep these nested serializers for validation and delegate the transaction to that service instead.

### Flat Update With Explicit Semantics

Prefer a flat update serializer when replacing or deleting nested children would be ambiguous:

```python
class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "email"]


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["phone", "notes"]
```

Expose profile and address updates through nested-router child endpoints unless the API has explicit, tested rules for omitted children, additions, updates, deletion, ordering, and PATCH behavior.

### Write Shape: `customer_profile: { ... }`

Use a nested object when the same request intentionally owns creation of the related object. This assumes the parent model has a forward `customer_profile` relation and the profile can be created independently; for a reverse One-to-One aggregate, use the earlier `CustomerCreateSerializer` shape.

Request:

```json
{
  "reference": "INV-2026-001",
  "customer_profile": {
    "name": "Ada Lovelace",
    "email": "ada@example.test"
  }
}
```

Serializer:

```python
from django.db import transaction
from rest_framework import serializers

from .models import BillingProfile, Invoice


class BillingProfileInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingProfile
        fields = ["name", "email"]


class InvoiceNestedProfileCreateSerializer(serializers.ModelSerializer):
    customer_profile = BillingProfileInputSerializer()

    class Meta:
        model = Invoice
        fields = ["id", "reference", "customer_profile"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data) -> Invoice:
        profile_data = validated_data.pop("customer_profile")
        request = self.context["request"]

        customer_profile = BillingProfile.objects.create(
            owner=request.user,
            **profile_data,
        )
        return Invoice.objects.create(
            owner=request.user,
            customer_profile=customer_profile,
            **validated_data,
        )
```

In `validated_data`, `customer_profile` is a dictionary because it came from a nested serializer. The explicit `create()` decides transaction scope and how the related row is persisted.

Do not use this shape when the client should select an existing profile, when profile creation has a separate permission boundary, or when deduplication and lifecycle rules belong to another service.

### Write Shape: `customer_profile_id: ...`

Use an ID field when the request links an existing related object. Use `PrimaryKeyRelatedField`, not a raw `IntegerField`, so existence and object conversion are handled during validation.

Request:

```json
{
  "reference": "INV-2026-002",
  "customer_profile_id": 42
}
```

Put reusable request-scoped relational fields beside the project's existing DRF utilities, for example in `api/fields.py` or `common/api/fields.py`.

### Utility: Context-Aware Primary Key Field

Keep the field generic: it only allows `queryset=` to be a callable that receives the serializer context. Domain scoping stays in a small named function beside the feature's selectors.

```python
from collections.abc import Callable
from typing import Generic, TypedDict, TypeVar, cast

from django.db.models import Model, QuerySet
from rest_framework import serializers
from rest_framework.request import Request


class SerializerContext(TypedDict, total=False):
    request: Request


ModelT = TypeVar("ModelT", bound=Model)
ContextQueryset = Callable[[SerializerContext], QuerySet[ModelT]]


class ContextPrimaryKeyRelatedField(
    serializers.PrimaryKeyRelatedField,
    Generic[ModelT],
):
    queryset: QuerySet[ModelT] | ContextQueryset[ModelT] | None

    def get_queryset(self) -> QuerySet[ModelT] | None:
        queryset = self.queryset
        if callable(queryset):
            return queryset(self.context)
        return cast(QuerySet[ModelT] | None, super().get_queryset())
```

The reusable field has no custom `__init__`, no owner assumptions, and no lookup DSL. The domain function owns the actual queryset:

```python
from django.db.models import QuerySet

from common.api.fields import SerializerContext

from .models import BillingProfile


def billing_profiles_for_context(context: SerializerContext) -> QuerySet[BillingProfile]:
    request = context.get("request")
    if request is None or not request.user.is_authenticated:
        return BillingProfile.objects.none()
    return BillingProfile.objects.filter(owner=request.user)
```

For tenant scoping, change only this function to follow the repository's tenant boundary. Do not add tenant, account, organization, and permission branches to the generic field.

Serializer with nested output and ID-based input:

```python
from rest_framework import serializers

from common.api.fields import ContextPrimaryKeyRelatedField

from .models import BillingProfile, Invoice
from .selectors import billing_profiles_for_context


class BillingProfileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingProfile
        fields = ["id", "name", "email"]


class InvoiceWriteSerializer(serializers.ModelSerializer):
    customer_profile = BillingProfileReadSerializer(read_only=True)
    customer_profile_id = ContextPrimaryKeyRelatedField[BillingProfile](
        source="customer_profile",
        queryset=billing_profiles_for_context,
        write_only=True,
    )

    class Meta:
        model = Invoice
        fields = ["id", "reference", "customer_profile", "customer_profile_id"]
        read_only_fields = ["id"]
```

Because `source="customer_profile"`, validated data contains the actual related instance:

```python
serializer.is_valid(raise_exception=True)
assert isinstance(serializer.validated_data["customer_profile"], BillingProfile)
invoice = invoice_create(
    owner=request.user,
    data=InvoiceCreateDTO(**serializer.validated_data),
)
```

`serializer.save(owner=request.user)` remains the mechanical CRUD path. Use the DTO only when a service owns the write and needs the resolved model.

The response can still return a nested object under `customer_profile`, while input uses only `customer_profile_id`:

```json
{
  "id": 10,
  "reference": "INV-2026-002",
  "customer_profile": {
    "id": 42,
    "name": "Ada Lovelace",
    "email": "ada@example.test"
  }
}
```

Scope the `PrimaryKeyRelatedField` queryset to the current tenant or owner. An unscoped `BillingProfile.objects.all()` field would allow linking another account's profile unless a separate permission layer prevents it.

### Accepting Either Nested Data Or An ID

Prefer separate endpoint serializers when possible. If one endpoint must accept either shape, map the two inputs to different internal keys, require exactly one, and choose the persistence path explicitly:

```python
class InvoiceFlexibleCreateSerializer(serializers.ModelSerializer):
    customer_profile = BillingProfileInputSerializer(
        required=False,
        write_only=True,
    )
    customer_profile_id = ContextPrimaryKeyRelatedField[BillingProfile](
        source="selected_customer_profile",
        queryset=billing_profiles_for_context,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Invoice
        fields = ["id", "reference", "customer_profile", "customer_profile_id"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        has_nested = "customer_profile" in attrs
        has_id = "selected_customer_profile" in attrs

        if has_nested == has_id:
            raise serializers.ValidationError(
                "Provide exactly one of customer_profile or customer_profile_id."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data) -> Invoice:
        request = self.context["request"]
        profile_data = validated_data.pop("customer_profile", None)
        selected_profile = validated_data.pop("selected_customer_profile", None)

        if profile_data is not None:
            selected_profile = BillingProfile.objects.create(
                owner=request.user,
                **profile_data,
            )

        assert selected_profile is not None
        return Invoice.objects.create(
            owner=request.user,
            customer_profile=selected_profile,
            **validated_data,
        )
```

Use a separate read serializer for the response so the output remains the stable nested representation. Test all four cases: nested only, ID only, both supplied, and neither supplied.

### Scoped Relation Utility Test

Test the security property owned by the field utility independently from the ViewSet. ORM setup is correct here because this is not an endpoint test:

```python
from types import SimpleNamespace

import pytest

from .models import BillingProfile
from .serializers import InvoiceWriteSerializer


@pytest.mark.django_db
def test_customer_profile_id_rejects_another_owner(user, other_user):
    other_profile = BillingProfile.objects.create(
        owner=other_user,
        name="Other account",
        email="other@example.test",
    )
    request = SimpleNamespace(user=user)
    serializer = InvoiceWriteSerializer(
        data={
            "reference": "INV-2026-003",
            "customer_profile_id": other_profile.pk,
        },
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "customer_profile_id" in serializer.errors
```

### ModelViewSet With Action-Specific Serializers

Use this `ModelViewSet` shape for simple CRUD only: list, retrieve, create, update, partial update, and delete of one resource. If an action coordinates business rules or side effects, call a service from an explicit endpoint rather than placing the workflow in serializer hooks.

```python
from django.db.models import QuerySet
from rest_framework import filters, permissions, viewsets
from rest_framework.serializers import BaseSerializer

from .models import Customer
from .serializers import (
    CustomerCreateSerializer,
    CustomerReadSerializer,
    CustomerUpdateSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    serializer_classes: dict[str, type[BaseSerializer]] = {
        "create": CustomerCreateSerializer,
        "update": CustomerUpdateSerializer,
        "partial_update": CustomerUpdateSerializer,
    }

    def get_queryset(self) -> QuerySet[Customer]:
        return (
            Customer.objects.filter(owner=self.request.user)
            .select_related("profile")
            .prefetch_related("addresses")
        )

    def get_serializer_class(self) -> type[BaseSerializer]:
        return self.serializer_classes.get(self.action, CustomerReadSerializer)

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(owner=self.request.user)
```

Keep `queryset = Customer.objects.none()` only if repository tooling requires a class-level queryset for schema generation. When `get_queryset()` owns the queryset, register the router with an explicit `basename`.

Use `ModelViewSet` only while list, retrieve, create, update, and destroy remain resource-shaped. Move workflows, side effects, approvals, and multi-step operations to services or explicit `@action`/APIView boundaries.

### Nested Relation ViewSets

When a related model has its own list, create, update, or delete operations, give it a child `ModelViewSet` and register it with `NestedSimpleRouter`. Do not hide that CRUD behind only a nested serializer field on the parent.

`lookup="customer"` on the nested router adds `customer_pk` to the URL kwargs. Filter the child queryset with that parent id and the same ownership scope as the parent. Bind the parent in `perform_create()` from the URL; do not accept a client-supplied parent id.

```python
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.serializers import BaseSerializer

from .models import Address, Customer, CustomerProfile
from .serializers import (
    AddressSerializer,
    CustomerProfileSerializer,
    CustomerProfileUpdateSerializer,
)


class CustomerProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_classes: dict[str, type[BaseSerializer]] = {
        "update": CustomerProfileUpdateSerializer,
        "partial_update": CustomerProfileUpdateSerializer,
    }

    def get_queryset(self) -> QuerySet[CustomerProfile]:
        return CustomerProfile.objects.filter(
            customer_id=self.kwargs["customer_pk"],
            customer__owner=self.request.user,
        )

    def get_serializer_class(self) -> type[BaseSerializer]:
        return self.serializer_classes.get(self.action, CustomerProfileSerializer)

    def perform_create(self, serializer: BaseSerializer) -> None:
        customer = get_object_or_404(
            Customer.objects.filter(owner=self.request.user),
            pk=self.kwargs["customer_pk"],
        )
        serializer.save(customer=customer)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self) -> QuerySet[Address]:
        return Address.objects.filter(
            customer_id=self.kwargs["customer_pk"],
            customer__owner=self.request.user,
        )

    def perform_create(self, serializer: BaseSerializer) -> None:
        customer = get_object_or_404(
            Customer.objects.filter(owner=self.request.user),
            pk=self.kwargs["customer_pk"],
        )
        serializer.save(customer=customer)
```

This follows the `drf-nested-routers` queryset pattern: the child filters with `self.kwargs["<lookup>_pk"]`. Prefer that explicit filter over `NestedViewSetMixin` so ownership scoping stays visible. One-to-One children still use the generated list and detail URLs.

### Router Registration

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import AddressViewSet, CustomerProfileViewSet, CustomerViewSet


router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="customer")

customers_router = NestedSimpleRouter(router, "customers", lookup="customer")
customers_router.register("profile", CustomerProfileViewSet, basename="customer-profile")
customers_router.register("addresses", AddressViewSet, basename="customer-address")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(customers_router.urls)),
]
```

This generates `/customers/`, `/customers/{pk}/`, `/customers/{customer_pk}/profile/`, `/customers/{customer_pk}/profile/{pk}/`, `/customers/{customer_pk}/addresses/`, and `/customers/{customer_pk}/addresses/{pk}/`.

Do not include a trailing slash in the router prefix. Use the generated names such as `customer-list`, `customer-detail`, `customer-address-list`, and `customer-address-detail` in tests. A nested `reverse()` needs `kwargs={"customer_pk": customer["id"]}` when the customer came from a `given_*` helper.

Use `NestedDefaultRouter` only when the nested collection should appear on a browsable API root. Prefer `NestedSimpleRouter` for child routes. For a second nesting level, wrap the child router the same way: `NestedSimpleRouter(customers_router, "addresses", lookup="address")`.

### Nested Response Shape

The read serializer produces a contract shaped like:

```json
{
  "id": 42,
  "name": "Ada Lovelace",
  "email": "ada@example.test",
  "profile": {
    "id": 3,
    "phone": "+55 11 0000-0000",
    "notes": "Prefers email"
  },
  "addresses": [
    {
      "id": 7,
      "label": "home",
      "city": "Sao Paulo",
      "country": "BR",
      "is_primary": true
    }
  ],
  "created_at": "2026-08-25T12:00:00Z",
  "updated_at": "2026-08-25T12:00:00Z"
}
```

### HTTP Given Helpers

Put reusable arrange helpers in `tests/helpers.py`. Name them `given_a_<resource>` or `given_an_<resource>`. Each helper POSTs through the already-authenticated client, asserts the setup status, and returns the public API representation. Do not plant endpoint-test state with `Model.objects.create` when a create API exists.

`given_a_customer` follows the create with a retrieve so later tests use the read contract, including nested ids.

```python
from typing import TypedDict

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class CustomerProfilePayload(TypedDict):
    phone: str
    notes: str


class AddressPayload(TypedDict):
    label: str
    city: str
    country: str
    is_primary: bool


def given_a_customer(
    *,
    api_client: APIClient,
    name: str = "Ada Lovelace",
    email: str = "ada@example.test",
    profile: CustomerProfilePayload | None = None,
    addresses: list[AddressPayload] | None = None,
):
    payload = {
        "name": name,
        "email": email,
        "profile": profile or {"phone": "123", "notes": ""},
    }
    if addresses is not None:
        payload["addresses"] = addresses

    created = api_client.post(reverse("customer-list"), payload, format="json")
    assert created.status_code == status.HTTP_201_CREATED

    detail = api_client.get(reverse("customer-detail", args=[created.data["id"]]))
    assert detail.status_code == status.HTTP_200_OK
    return detail.data


def given_an_address(
    *,
    api_client: APIClient,
    customer_id: int,
    label: str = "home",
    city: str = "London",
    country: str = "GB",
    is_primary: bool = True,
):
    response = api_client.post(
        reverse("customer-address-list", kwargs={"customer_pk": customer_id}),
        {
            "label": label,
            "city": city,
            "country": country,
            "is_primary": is_primary,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.data
```

### API Tests For Nested CRUD

Structure each endpoint test as Given / When / Then. Given uses `given_*` helpers. When is the endpoint under test. Then asserts HTTP status and body, then a follow-up GET when the test needs persisted or scoped state.

```python
import pytest
from django.urls import reverse
from rest_framework import status

from .helpers import given_a_customer, given_an_address


@pytest.mark.django_db
def test_customer_detail_returns_nested_relations(api_client, user):
    api_client.force_authenticate(user)

    # given
    customer = given_a_customer(
        api_client=api_client,
        addresses=[
            {
                "label": "home",
                "city": "London",
                "country": "GB",
                "is_primary": True,
            }
        ],
    )

    # when
    response = api_client.get(reverse("customer-detail", args=[customer["id"]]))

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.data["profile"]["phone"] == "123"
    assert response.data["addresses"][0]["label"] == "home"


@pytest.mark.django_db
def test_customer_create_persists_nested_relations(api_client, user):
    api_client.force_authenticate(user)

    # given
    payload = {
        "name": "Ada Lovelace",
        "email": "ada@example.test",
        "profile": {"phone": "123", "notes": ""},
        "addresses": [
            {
                "label": "home",
                "city": "London",
                "country": "GB",
                "is_primary": True,
            }
        ],
    }

    # when
    response = api_client.post(reverse("customer-list"), payload, format="json")

    # then
    assert response.status_code == status.HTTP_201_CREATED
    detail = api_client.get(reverse("customer-detail", args=[response.data["id"]]))
    assert detail.status_code == status.HTTP_200_OK
    assert detail.data["profile"]["phone"] == "123"
    assert detail.data["addresses"][0]["city"] == "London"


@pytest.mark.django_db
def test_address_list_is_scoped_to_the_parent_customer(api_client, user):
    api_client.force_authenticate(user)

    # given
    customer = given_a_customer(api_client=api_client)
    other = given_a_customer(
        api_client=api_client,
        name="Other",
        email="other@example.test",
    )
    given_an_address(
        api_client=api_client,
        customer_id=customer["id"],
        label="home",
        city="London",
    )
    given_an_address(
        api_client=api_client,
        customer_id=other["id"],
        label="office",
        city="Paris",
        country="FR",
    )

    # when
    response = api_client.get(
        reverse("customer-address-list", kwargs={"customer_pk": customer["id"]})
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert [row["city"] for row in response.data] == ["London"]


@pytest.mark.django_db
def test_address_create_binds_the_parent_from_the_url(api_client, user):
    api_client.force_authenticate(user)

    # given
    customer = given_a_customer(api_client=api_client)

    # when
    response = api_client.post(
        reverse("customer-address-list", kwargs={"customer_pk": customer["id"]}),
        {
            "label": "home",
            "city": "London",
            "country": "GB",
            "is_primary": True,
        },
        format="json",
    )

    # then
    assert response.status_code == status.HTTP_201_CREATED
    listed = api_client.get(
        reverse("customer-address-list", kwargs={"customer_pk": customer["id"]})
    )
    assert listed.status_code == status.HTTP_200_OK
    assert listed.data[0]["id"] == response.data["id"]
    assert listed.data[0]["city"] == "London"


@pytest.mark.django_db
def test_profile_update_uses_the_nested_router(api_client, user):
    api_client.force_authenticate(user)

    # given
    customer = given_a_customer(api_client=api_client)

    # when
    response = api_client.patch(
        reverse(
            "customer-profile-detail",
            kwargs={
                "customer_pk": customer["id"],
                "pk": customer["profile"]["id"],
            },
        ),
        {"notes": "Prefers email"},
        format="json",
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    detail = api_client.get(reverse("customer-detail", args=[customer["id"]]))
    assert detail.data["profile"]["notes"] == "Prefers email"
```

Add wrong-owner tests to prove `get_queryset()` prevents cross-account retrieve, update, and delete on both parent and nested routes. Plant the other account through a second authenticated client and its own `given_*` helpers. Add query-count coverage when nested list performance is a material risk.

### Nested CRUD Completion Checklist

- Models use intentional `on_delete` behavior and useful `related_name` values.
- Read serializers declare nested OtO and OtM fields explicitly.
- To-many nested fields use `many=True`.
- Writable nesting has explicit transactional create/update semantics.
- Related-resource CRUD uses `NestedSimpleRouter` child ViewSets scoped by `self.kwargs["<lookup>_pk"]`.
- Nested `perform_create()` binds the parent from the URL, not from the request body.
- Ambiguous child updates use nested-router endpoints, not an implicit parent PATCH.
- ID-based inputs reuse a small context-aware relational field instead of serializer-specific `__init__` mutation.
- ViewSet querysets are ownership-scoped before lookup.
- Querysets match serializer relations with `select_related` and `prefetch_related`.
- Serializer selection matches `list`, `retrieve`, `create`, `update`, and `partial_update` contracts.
- Router `basename` and test route names are explicit, including nested names such as `customer-address-list`.
- Tests arrange via `given_*` HTTP helpers and follow Given / When / Then.

## Django

Django and DRF patterns for models, services, selectors, serializers, endpoints, routing, and tests.

### When To Use

Use for Django, DRF, models, services, selectors, serializers, endpoints, routing, migrations, and Django testing.

### Core Rules

- Inspect existing Django app, model, serializer, endpoint, and test conventions first.
- Keep reads and writes in the same boundaries the repo already uses.
- Read this complete topic before applying its guidance to the touched Django boundary.

### Preferred Patterns

- Thin DRF views or viewsets.
- Explicit service boundaries for writes.
- Selectors or equivalent read-side patterns when the repo uses them.
- `NestedSimpleRouter` child ViewSets for related-resource CRUD.
- Route and serializer patterns that match nearby code.

### Anti-Patterns

- New Django abstractions that duplicate the local pattern.
- Business logic hidden in serializers or models when the repo uses services.
- Broad edits that change multiple Django conventions at once.

### Checklist

- Identify the affected Django boundary.
- Inspect matching local examples.
- Apply only the sections relevant to the change after reading the complete topic.
- Validate with focused Django or DRF tests.

---

### Django Project Bootstrap

Use this section when the user wants a fresh Django codebase or backend/API project from the personal template.

#### Rules

- Template repo: `https://github.com/Mires/django-cookiecutter-standard`.
- Prefer HTTPS and use `git@github.com:Mires/django-cookiecutter-standard.git` only when SSH access is required.
- Generate a new project directory without editing the template repository.
- Do not install dependencies, create virtualenvs, run migrations, or start services unless the user asks.
- If template variables are already known, prefer a non-interactive invocation with explicit key/value overrides.
- Ask only for missing project-specific fields when the template prompts for values not provided.

#### Workflow

1. Run Cookiecutter directly against the HTTPS URL.
2. If `cookiecutter` is missing and `uvx` exists, run it through `uvx --from cookiecutter`.
3. If HTTPS is blocked by required SSH access, verify SSH with `git ls-remote` before retrying.
4. Verify the expected output directory exists and stop after bootstrap.

#### Commands

```bash
cookiecutter https://github.com/Mires/django-cookiecutter-standard
uvx --from cookiecutter cookiecutter https://github.com/Mires/django-cookiecutter-standard
git ls-remote git@github.com:Mires/django-cookiecutter-standard.git HEAD
```

---

### Django Models AppConfig Admin

Use this section when a Django model change needs app configuration or admin registration.

#### Rules

- Ensure each app `apps.py` declares `default_auto_field = "django.db.models.BigAutoField"`.
- Set the app config `name` to the full `apps.<app_name>` path used by the project.
- Register every model in `admin.py` with the decorator pattern.
- Use useful `list_display`, `list_filter`, `search_fields`, `readonly_fields`, and `ordering` values.
- Keep admin imports local to the app model module.

#### Example

```python
from django.contrib import admin

from apps.example.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ["-created_at"]
```

---

### Django Models Base Classes

Use this section when adding or changing a Django model class.

#### Rules

- Inspect the app `models.py`, `admin.py`, `apps.py`, and migrations before introducing new model patterns.
- Use `AppBaseModel` for standalone entities.
- Use `AppBaseModel, AccountRelatedModel` for account-scoped entities.
- Use `AppBaseModel` for junction or through models unless the local app already does something different.
- Import shared base classes from `apps.common.models` and account scope from `apps.account.models` when those modules exist.

#### Example

```python
from apps.account.models import AccountRelatedModel
from apps.common.models import AppBaseModel


class ExampleModel(AppBaseModel, AccountRelatedModel):
    ...
```

---

### Django Models Fields Relationships

Use this section when adding fields or relations to a Django model.

#### Rules

- Reuse existing field names, related names, and model organization when possible.
- Use string references for cross-app relations to avoid circular imports.
- Use `blank=True, default=""` for optional text fields when that matches the app style.
- Use `null=True, blank=True` for optional foreign keys that can be absent.
- Set explicit `related_name` values that are easy to grep.
- Do not redeclare `created_at` or `updated_at`; shared base models provide them.

#### Example

```python
from django.db import models


name = models.CharField(max_length=255)
description = models.TextField(blank=True, default="")
is_active = models.BooleanField(default=True)
related = models.ForeignKey(
    "other_app.OtherModel",
    on_delete=models.CASCADE,
    related_name="examples",
)
optional_ref = models.ForeignKey(
    "other_app.OtherModel",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="optional_examples",
)
```

---

### Django Models Migrations

Use this section after changing Django model fields, constraints, relationships, or model classes.

#### Rules

- Create migrations when model state changes.
- Inspect generated migrations before applying them.
- Update `admin.py` and `apps.py` when a new model or app shape requires it.
- Update serializers, selectors, views, services, and tests that expose the model.
- Run the project's established migration commands when available; otherwise use `uv run python manage.py makemigrations` and `uv run python manage.py migrate`.

#### Checklist

- Migration exists for model changes.
- Admin and app config are still correct.
- User-visible model behavior has tests or manual validation.

---

### Django Models Special Fields

Use this section when a Django model needs derived values, embeddings, or non-standard fields.

#### Rules

- Use `@property` for derived values that do not need storage.
- Only use `VectorField` when the app already uses pgvector or the task explicitly requires embeddings.
- Keep embedding dimensions and vector behavior aligned with the existing app configuration.
- Do not store a computed value unless queries, constraints, or performance make persistence necessary.
- Add tests around public behavior that depends on specialized fields.

#### Examples

```python
@property
def is_valid(self) -> bool:
    return bool(self.upload_finished_at)
```

```python
from pgvector.django import VectorField

embedding = VectorField(dimensions=1536)
```

---

### Django Models Str Timestamps

Use this section when implementing model display, ordering, or timestamp behavior.

#### Rules

- Always use `fmt_model_str` for `__str__` when the repo provides it.
- Include stable fields such as `id`, `name`, or a useful foreign-key traversal in the display fields.
- Foreign-key traversal such as `user__email` is allowed when it improves readability.
- Set `Meta.ordering = ["-created_at"]` when the model needs the repo-standard newest-first ordering.
- Do not redeclare timestamp fields inherited from `AppBaseModel`.

#### Example

```python
from apps.common.models import fmt_model_str


def __str__(self) -> str:
    return fmt_model_str(self, fields=["id", "name"])


class Meta:
    ordering = ["-created_at"]
```

---

### Django Services Boundaries

Use this section when deciding where Django business logic belongs.

#### Rules

- Keep endpoints thin: validate input, call a selector or service, return a response.
- Keep serializers focused on validation and representation, not business writes.
- Keep services focused on pushing state changes, business rules, and side effects.
- Class-based services take other services or clients in `__init__`. Pass Django models into methods, never into the constructor.
- Do not hide write-side business logic in views, serializers, managers, querysets, model `save()`, or signals.
- If a service becomes read-heavy and stops mutating state, move the fetch logic into a selector.
- Start with `services.py`; split into a `services/` package only when the app grows multiple service domains.

---

### Django Services Dependencies

Use this section when a Django service needs other services, selectors, tasks, repositories, or external clients.

#### Rules

- Inject other services and external clients through the service constructor when the service is a class.
- Never accept a Django model in `__init__` or store one on the service instance. Pass models into methods.
- Call selectors for read-heavy checks or visibility queries instead of duplicating fetch logic.
- Allow methods to call model methods, external clients, and async tasks when those collaborators were injected or passed in.
- Keep request and response objects out of services.
- Obtain SDK clients through the project dependency layer at the edge, then inject them into the service.

---

### Django Services Exceptions

Use this section when service failures need a domain-specific exception or HTTP-facing translation.

#### Rules

- Use exceptions from `apps.common.exceptions` when the project provides them.
- Raise explicit business exceptions with human-readable messages when an invariant fails.
- Add a new exception type in `apps/common/exceptions.py` when callers need a distinct status code or error code.
- Preserve the project spelling of existing base exception classes, including `BussinesLogicException` if that is what the repo defines.
- Do not hide invalid business state in booleans or `None` returns when callers need an actionable error.

#### Example

```python
from apps.common.exceptions import BussinesLogicException


def do_something(*, instance) -> None:
    if not instance.is_valid:
        raise BussinesLogicException("Custom message")
```

---

### Django Services Flow Services

Use this section when service behavior spans a multi-step workflow or shared dependencies.

#### Rules

- Use plain functions for most mutations.
- Use a class when the service represents a multi-step flow or needs another service as a constructor dependency.
- If the existing app already uses a `services/` package or class-based flow services, follow that local shape.
- Keep each method explicit, typed, and transaction-aware.
- Do not turn ordinary create/update/delete behavior into a class just for organization.
- Constructor parameters are other services or clients. Method parameters carry models, ids, serializer fields, and DTOs.

#### Example

```python
class ExampleNotificationService:
    def notify_export_started(self, *, export: ExampleExport) -> None:
        export_started_task.delay(export_id=export.id)


class ExampleExportService:
    def __init__(self, *, notification_service: ExampleNotificationService) -> None:
        self.notification_service = notification_service

    @transaction.atomic
    def start(self, *, account: Account, name: str) -> ExampleExport:
        export = ExampleExport(account=account, name=name, status="pending")
        export.full_clean()
        export.save()
        transaction.on_commit(
            lambda: self.notification_service.notify_export_started(export=export)
        )
        return export
```

---

### Django Services Functions

Use this section when adding write-side business logic in a Django app.

#### Rules

- Services own business rules, state changes, and side effects.
- Prefer function-based services by default.
- Use keyword-only arguments unless the service takes zero or one argument.
- Type annotate service inputs and return values.
- When the caller is a serializer, accept the validated fields and call the service with `**serializer.validated_data`.
- When the caller already has a Pydantic DTO, persist or forward it with `**data.model_dump()`.
- Prefer names such as `invoice_create`, `invoice_send`, or `invoice_cancel`.
- Call `full_clean()` before `save()` when the service owns persistence for new or materially changed models.

#### Example

```python
from apps.example.models import ExampleModel


def example_create(*, account, name: str) -> ExampleModel:
    example = ExampleModel(account=account, name=name)
    example.full_clean()
    example.save()
    return example
```

Call this as `example_create(account=account, **serializer.validated_data)` from a view or serializer. If the caller already has a Pydantic DTO, use `example_create(account=account, **data.model_dump())`.

---

### Django Services Transactions

Use this section when a Django service writes multiple rows, enforces invariants, or dispatches side effects.

#### Rules

- Use `@transaction.atomic` when the service writes multiple rows, enforces invariants, or coordinates related mutations.
- Keep transaction boundaries in the service layer instead of the serializer layer.
- Use `transaction.on_commit()` for side effects that should only run after the database commit succeeds.
- Do not enqueue tasks, send emails, or call external systems before the database state they depend on is durable.
- Test both successful persistence and relevant failure behavior.

#### Example

```python
from django.db import transaction


@transaction.atomic
def example_create(*, account, name: str):
    example = ExampleModel(account=account, name=name)
    example.full_clean()
    example.save()
    transaction.on_commit(lambda: example_created_task.delay(example_id=example.id))
    return example
```

---

### Django Selectors Boundaries

Use this section when deciding what belongs in a selector.

#### Rules

- Selectors may compose other selectors.
- Selectors do not mutate database state or trigger business side effects.
- Selectors may populate a cache on a read miss when that cache write is only a read optimization.
- Services may call selectors to enforce read-side rules before mutating data.
- Endpoints may use selectors directly for read-only flows.
- Prefer names such as `invoice_get`, `invoice_list`, or `invoice_get_visible_for`.
- Start with `selectors.py`; split into a `selectors/` package when query surface grows by domain.

---

### Django Selectors Cached

Use this section when the same Django read path is hot and the repo already uses caching for similar lookups.

#### Rules

- Keep cache reads and writes inside the selector when caching is only a read optimization.
- Prefer caching a read model or serialized payload instead of a live ORM instance unless the repo already caches model instances intentionally.
- Use explicit cache keys and timeout constants.
- Return the same shape on cache hits and database misses.
- Do not hide business side effects inside a cached selector.

---

### Django Selectors Detail

Use this section when adding reusable read access to one object or a scoped queryset.

#### Rules

- Selectors own read paths, filtering, query composition, and queryset optimization.
- Use keyword-only arguments unless the selector takes zero or one argument.
- Type annotate selector inputs and return values.
- Use account, user, or visibility scope in the selector when access rules require it.
- Be consistent about missing-object behavior: return `None`, return a queryset for endpoint `get_object_or_404`, or raise a repo-standard exception.

#### Example

```python
def example_get(*, example_id, account) -> ExampleModel | None:
    return (
        ExampleModel.objects.select_related("account")
        .prefetch_related("tags")
        .filter(id=example_id, account=account)
        .first()
    )
```

---

### Django Selectors List

Use this section when building list endpoints or reusable filtered queryset logic.

#### Rules

- Keep filtering and optimization in selectors instead of scattering it across views.
- Use `django_filters.FilterSet` when the repo uses django-filter for request filters.
- Apply account or user scope before returning a queryset.
- Set stable ordering in the selector when endpoint order matters.
- Return the shape that best fits the caller: queryset, list, dict, or computed collection.

#### Example

```python
class ExampleFilter(django_filters.FilterSet):
    class Meta:
        model = ExampleModel
        fields = ("status", "is_active")


def example_list(*, account, filters: dict | None = None):
    filters = filters or {}
    queryset = ExampleModel.objects.filter(account=account).order_by("-created_at")
    return ExampleFilter(filters, queryset).qs
```

---

### Django Selectors Optimization

Use this section when a read path risks N+1 queries, heavy annotations, or repeated filtering logic.

#### Rules

- Use `select_related()` for foreign keys and one-to-one relationships that would otherwise cause N+1 queries.
- Use `prefetch_related()` for many-to-many and reverse relationships.
- Keep heavy read-path annotations, filtering, and ordering logic in selectors.
- If a computed model property spans multiple relations or would cause N+1 queries during serialization, prefer a selector instead.
- Align optimizations with the response serializer fields and nested representations.

---

### Django Serializers Action Aware

Use this section when a ViewSet needs different serializers for list, retrieve, create, or custom actions.

#### Rules

- Implement `get_serializer_class()` explicitly when a ViewSet needs per-action serializers.
- Keep a `serializer_action_classes` map on the ViewSet when that matches local style.
- If one action has different input and output serializers, validate with the input serializer and instantiate the output serializer for the response.
- Keep action serializer choices close to the ViewSet so routes remain easy to inspect.
- Do not make a single serializer carry unrelated request and response responsibilities.

---

### Django Serializers Advanced Functions

Use this section when response assembly is more complex than a single serializer instantiation.

#### Rules

- Move complex output assembly into a serializer function instead of overloading a selector.
- Let selectors decide what data to fetch and serializer functions decide how to shape API-ready payloads.
- Optimize related objects deliberately before serializing lists or feeds.
- Keep serializer functions close to serializer classes unless the repo has a better module convention.
- Test the response shape through the endpoint or a focused serializer test.

#### Example

```python
def example_feed_serialize(feed):
    feed_ids = [item.id for item in feed]
    objects = ExampleModel.objects.filter(id__in=feed_ids).order_by("-created_at")
    return [ExampleSerializerResponse(obj).data for obj in objects]
```

---

### Django Serializers Boundaries

Use this section when deciding what logic belongs in a DRF serializer.

#### Rules

- Serializer code should validate input and shape output; it should not become the home of business writes.
- Do not move business writes into `create()` or `update()` unless the repo already treats that serializer as a thin adapter over a service.
- Do not hide orchestration, task dispatch, or side effects in `validate()`.
- Pass `context` only when the serializer genuinely needs request-aware behavior for representation or validation.
- Keep nested serializers and computed fields readable; if output optimization grows complex, refetch and serialize deliberately.

---

### Django Serializers Input

Use this section when an endpoint needs request-body, query-parameter, or action-payload validation.

#### Rules

- Use a dedicated input serializer when the endpoint accepts structured data.
- Use `serializers.Serializer` for request payloads, query params, custom action payloads, and non-trivial validation flows.
- Keep validation in serializers and business rules in services.
- Use `validate_<field>` for per-field normalization and `validate()` for cross-field validation.
- Use `raise_exception=True` when validating in views or actions.

#### Example

```python
from rest_framework import serializers


class ExampleSerializerRequest(serializers.Serializer):
    name = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        return value.strip()
```

---

### Django Serializers Output

Use this section when shaping data returned from a DRF endpoint.

#### Rules

- Use a dedicated output serializer when an endpoint returns structured data.
- Use `ModelSerializer` for straightforward read representations or when the app already exposes the model directly.
- Set explicit `fields` and mark response fields read-only when appropriate.
- Use plain `Serializer` for computed outputs or responses that do not map cleanly to one model.
- Serialize output explicitly in the endpoint instead of relying on hidden side effects.

#### Example

```python
class ExampleSerializerResponse(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = ["id", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = fields
```

---

### Django Endpoints APIView

Use this section when an endpoint is custom logic rather than standard resource CRUD.

#### Rules

- Use an APIView for bespoke workflows, RPC-like actions, webhooks, or multi-step flows.
- Inspect existing `views.py`, `serializers.py`, `selectors.py`, `services.py`, `urls.py`, and tests before choosing the shape.
- Validate request data with a serializer and `raise_exception=True`.
- Call a selector for read flows and a service for write flows.
- Return `Response(..., status=...)` explicitly.
- Use the project base APIView when one exists.

#### Example

```python
class ExampleAPIView(BaseAPIView):
    def post(self, request: Request) -> Response:
        input_serializer = ExampleSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        example = services.do_example(**input_serializer.validated_data)
        output_serializer = ExampleSerializerResponse(example)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```

---

### Django Endpoints CRUD ViewSets

Use this section when an endpoint maps to standard resource CRUD or partial CRUD.

#### Rules

- Use `ReadOnlyModelViewSet` for router-backed list/retrieve behavior.
- Use `GenericViewSet` plus mixins for create-only, list-only, list-create, or other partial CRUD shapes.
- Use `ModelViewSet` only when CRUD is genuinely mechanical or the app already uses it for that resource.
- Register related-resource CRUD on a `NestedSimpleRouter` child ViewSet instead of stretching parent serializer writes.
- Create shared mixin combinations only when partial CRUD repeats across the repo.
- Drop to an APIView when the workflow does not map cleanly to resource CRUD.

#### Curated ViewSet Shapes

- `ModelViewSet`
- `ReadOnlyModelViewSet`
- `CreateViewSet`
- `ListViewSet`
- `RetrieveViewSet`
- `UpdateViewSet`
- `DestroyViewSet`
- `ListCreateViewSet`
- `CreateListRetrieveViewSet`
- `RetrieveUpdateDestroyViewSet`

---

### Django Endpoints Responses

Use this section when finishing endpoint response behavior.

#### Rules

- Return explicit status codes for both success and failure paths.
- Serialize output explicitly instead of relying on hidden serializer side effects.
- For public endpoints, set `permission_classes = []` and `authentication_classes = []`.
- For read-only endpoints, prefer `self.get_object()`, `self.get_queryset()`, or selectors that keep object fetching consistent with the rest of the app.
- Keep pagination, filtering, and queryset optimization aligned with existing base views or pagination classes.
- Tests should assert both status code and response body.

---

### Django Endpoints Routing

Use this section when wiring DRF ViewSets and routes.

#### Rules

- Register router prefixes without a trailing slash.
- If the ViewSet omits a class-level `queryset`, provide `basename=` when registering it with the router.
- Register ViewSets with a router instead of wiring `@action` methods manually.
- Use `NestedSimpleRouter` when a related resource has its own list, create, update, or delete under a parent.
- Filter nested ViewSets with `self.kwargs["<lookup>_pk"]` and the same ownership scope as the parent.
- Bind the parent in `perform_create()` from the URL kwargs; do not trust a client-supplied parent id.
- Include both the parent router URLs and every nested router URL list.
- Keep action-specific settings such as `serializer_class`, `permission_classes`, `url_path`, and `detail` on the `@action` itself.
- Use `reverse()` with route names in tests instead of hardcoded URLs.

#### Example

```python
from rest_framework.routers import DefaultRouter

from apps.example.views import ExampleViewSet

router = DefaultRouter()
router.register("examples", ExampleViewSet, basename="example")

urlpatterns = router.urls
```

#### Nested Relation Example

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.example.views import ExampleItemViewSet, ExampleViewSet

router = DefaultRouter()
router.register("examples", ExampleViewSet, basename="example")

examples_router = NestedSimpleRouter(router, "examples", lookup="example")
examples_router.register("items", ExampleItemViewSet, basename="example-item")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(examples_router.urls)),
]
```

---

### Django Endpoints Service First CRUD

Use this section when CRUD behavior has branches, side effects, or cross-model rules.

#### Rules

- Override the action method or prefer an APIView instead of pushing business writes into serializer hooks.
- Use selectors in `get_queryset()` for read scope and optimization.
- Use an input serializer for validation and an output serializer for the response when they differ.
- Call the service from the action method and return an explicit status code.
- Use `ModelViewSet` only while create, update, and destroy remain straightforward.

---

### Django Endpoints ViewSet Actions

Use this section when behavior belongs on an existing resource.

#### Rules

- Use `@action` when the behavior is adjacent to an existing ViewSet resource.
- Set action-specific `detail`, `methods`, `serializer_class`, and `url_path` on the decorator.
- Use `self.get_serializer(data=request.data)` for action input when the decorator provides the serializer.
- Use `self.get_object()` for detail actions when the action mutates or reads the current resource.
- Call a service for writes and serialize output explicitly.

---

### Django Tests Given When Then

Use this section when writing an authenticated DRF endpoint test.

#### Rules

- Structure the test as `# given`, `# when`, `# then`.
- Given arranges state through `given_a_<resource>` or `given_an_<resource>` helpers that call the public create API.
- When is the single endpoint under test.
- Then asserts HTTP status and body. For mutations or scoping, prove the result with a follow-up GET on the public API.
- Keep the client authenticated before calling `given_*` helpers.
- Do not plant endpoint-test state with `Model.objects.create` when a create API exists.
- Use ORM setup only for isolated serializer, selector, service, or constraint tests, or for state the API cannot create.

---

### Django Tests Authenticated API

Use this section when testing an authenticated DRF endpoint.

#### Rules

- Use the project authenticated API client fixture when available, commonly `api_client_with_common_user`.
- Destructure the tuple into `api_client, user` for clarity.
- Use `reverse()` with the real route name.
- Assert the HTTP status code and full response body.
- For mutations, prove the result with a follow-up GET on the public API.
- Assert database state only when the behavior is not visible over HTTP.
- Use `@pytest.mark.django_db` on tests that touch the database.

---

### Django Tests DRF Rules

Use this section as the checklist for DRF endpoint tests.

#### Rules

- Use `@pytest.mark.django_db` on every test that touches the database.
- Use `reverse()`, never hardcoded URLs.
- Assert both HTTP status and response body.
- Arrange through `given_*` HTTP helpers when the public API can create the resource.
- For mutations, prove the result with a follow-up GET on the public API.
- Mock external services at the module where they are used.
- For list endpoints, assert the paginated response shape used by the repo.

---

### Django Tests Forbidden Patterns

Use this section as a negative checklist for Django tests.

#### Rules

- Do not use `factory_boy`.
- Do not use model factories of any kind.
- Do not use Django fixture files such as `.json`, `.yaml`, or `.xml`.
- Do not arrange endpoint tests with `Model.objects.create` when a public create API exists.
- Do not hardcode URLs.
- Do not skip response-body assertions on API tests.
- Do not hide important setup inside opaque fixtures when a helper would make the flow clearer.
- If a factory seems convenient, create a `given_*` helper instead.

---

### Django Tests Helpers Fixtures

Use this section when setting up reusable Django test state.

#### Rules

- Name arrange helpers `given_a_<resource>` or `given_an_<resource>`.
- Implement them as authenticated HTTP calls against the public API when that API can create the resource.
- Assert the setup status inside the helper and return `response.data`, or a follow-up GET when the read contract differs from create.
- Helpers should use keyword-only arguments and sensible defaults.
- If setup is missing, add or extend `tests/helpers.py` instead of creating one-off ORM setup inline.
- Fixtures should wrap helpers, authenticated clients, or other common setup utilities.
- Fixtures should not replace helpers with hidden ORM-heavy setup.
- Expected shared fixtures often include `api_client`, `common_user`, and `api_client_with_common_user`.

---

### Django Tests Mocking External Services

Use this section when a Django test touches email, task queues, SDK clients, HTTP APIs, storage, or other external systems.

#### Rules

- Mock external services at the module where the function is used, not where it is defined.
- Use fakes or `MagicMock` only at true external boundaries.
- Keep patching near the test that needs it.
- Set return values explicitly so assertions describe the behavior.
- Do not mock the service or selector under test unless the test is for an endpoint adapter boundary.

#### Example

```python
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
@patch.object(external_module, "method_name")
def test_action_returns_expected_result(mock_method: MagicMock, api_client_with_common_user):
    """Action returns expected data when the external service succeeds."""
    mock_method.return_value = {"key": "value"}
```

---

### Django Tests Naming Structure

Use this section when creating or reorganizing Django tests.

#### Rules

- Use `src/apps/<app>/tests/` with `__init__.py`, `helpers.py`, and `test_<feature>.py` when the repo follows that layout.
- Name tests with `test_<resource>_<action>_<condition>_<expected_result>`.
- Give every test a one-line docstring describing the behavior under test.
- Keep route names and helper imports consistent with nearby tests.
- Use app-level `conftest.py` only for fixtures that are genuinely shared.

#### Examples

- `test_register_returns_201_when_valid_data`
- `test_register_returns_400_when_email_already_exists`
- `test_me_returns_401_when_not_authenticated`

---

### Django Tests Pagination

Use this section when testing DRF list endpoints.

#### Rules

- Assert the full paginated response shape, not just the results array.
- Use the repo pagination convention for `next`, `previous`, and `results`.
- Assert ordering when list order is part of the endpoint contract.
- Create enough data to prove filtering, scope, or pagination behavior when relevant.
- Keep list setup in `given_*` helpers when it repeats across tests.

#### Expected Shape

```python
assert response.json() == {
    "next": None,
    "previous": None,
    "results": [...],
}
```

---

### Django Tests TDD Workflow

Use this section when adding tests for Django models, serializers, views, services, or DRF endpoints.

#### Rules

- Inspect the app `tests/`, `helpers.py`, and `conftest.py` before adding setup code.
- Reuse existing `given_*` helper names, auth fixtures, route naming, and response assertion style.
- Start from user-visible behavior or the API contract.
- Make the smallest production change that satisfies the failing test.
- Move repeated HTTP setup into `tests/helpers.py` as `given_*` helpers during refactor.

#### Workflow

1. RED: write the failing behavior test first.
2. GREEN: implement the smallest code change.
3. REFACTOR: improve repeated setup and helper clarity.

---

### Django Tests Unauthenticated API

Use this section when testing access behavior without credentials.

#### Rules

- Use the unauthenticated `api_client` fixture.
- Use `reverse()` with the real route name.
- Assert `HTTP_401_UNAUTHORIZED` for endpoints requiring authentication unless the repo expects `403` for that path.
- For public endpoints, assert the public success or validation response explicitly.
- Do not rely on hardcoded URL strings.

#### Example

```python
@pytest.mark.django_db
def test_resource_returns_401_when_not_authenticated(api_client: APIClient) -> None:
    """GET resource returns 401 when no auth token is provided."""
    url = reverse("api:example:example-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Django Standard Handbook

This section is the complete Django backend/API handbook (formerly the `django-cookiecutter-standard` repository), merged into this skill. Each `### path` subsection is one original handbook document; `<!-- artifact: ... -->` markers name the file each canonical fence reconstructs. The reference snapshot is Python 3.14.6, Django 6.0.7, and Django REST framework 3.17.1.

How to use it:

- Find the subsection for the boundary you are touching (model, service, selector, view, serializer, settings, recipe, or test) and adapt its canonical fence to the target repository.
- Prefer direct Django/DRF CRUD. Use services for transactions or side effects and selectors for reusable complex reads. Do not add repository or use-case layers.
- Scope every account-owned query before lookup or mutation, and test tenant isolation and authorization failures.
- Cross-app consumers import only the owning app's `dtos.py` and its service or selector functions; cross-app reads return DTOs, never a model instance or `QuerySet`.
- Credentials are environment variables. Never commit secrets or generated code.

### Handbook Contents

- [README.md](#readmemd)
- [AGENTS.md](#agentsmd)
- [docs/api-design.md](#docsapi-designmd)
- [docs/architecture.md](#docsarchitecturemd)
- [docs/conventions.md](#docsconventionsmd)
- [docs/operations.md](#docsoperationsmd)
- [docs/reconstruction.md](#docsreconstructionmd)
- [docs/security.md](#docssecuritymd)
- [docs/testing.md](#docstestingmd)
- [docs/version-snapshot.md](#docsversion-snapshotmd)
- [docs/view-patterns.md](#docsview-patternsmd)
- [compose-dev.md](#compose-devmd)
- [compose.md](#composemd)
- [conftest.md](#conftestmd)
- [dockerfile.md](#dockerfilemd)
- [environment.md](#environmentmd)
- [gitignore.md](#gitignoremd)
- [gunicorn.conf.md](#gunicornconfmd)
- [makefile.md](#makefilemd)
- [pre-commit-config.md](#pre-commit-configmd)
- [pyproject.md](#pyprojectmd)
- [pytest.md](#pytestmd)
- [python-version.md](#python-versionmd)
- [uv-lock.md](#uv-lockmd)
- [src/README.md](#srcreadmemd)
- [src/apps/README.md](#srcappsreadmemd)
- [src/apps/account/README.md](#srcappsaccountreadmemd)
- [src/apps/account/admin.md](#srcappsaccountadminmd)
- [src/apps/account/apps.md](#srcappsaccountappsmd)
- [src/apps/account/models.md](#srcappsaccountmodelsmd)
- [src/apps/account/services.md](#srcappsaccountservicesmd)
- [src/apps/api/README.md](#srcappsapireadmemd)
- [src/apps/api/apps.md](#srcappsapiappsmd)
- [src/apps/api/exceptions.md](#srcappsapiexceptionsmd)
- [src/apps/api/health.md](#srcappsapihealthmd)
- [src/apps/api/middleware.md](#srcappsapimiddlewaremd)
- [src/apps/api/pagination.md](#srcappsapipaginationmd)
- [src/apps/api/tests/README.md](#srcappsapitestsreadmemd)
- [src/apps/api/tests/views/README.md](#srcappsapitestsviewsreadmemd)
- [src/apps/api/tests/views/test_health.md](#srcappsapitestsviewstest_healthmd)
- [src/apps/api/urls.md](#srcappsapiurlsmd)
- [src/apps/api/views.md](#srcappsapiviewsmd)
- [src/apps/authentication/README.md](#srcappsauthenticationreadmemd)
- [src/apps/authentication/admin.md](#srcappsauthenticationadminmd)
- [src/apps/authentication/apps.md](#srcappsauthenticationappsmd)
- [src/apps/authentication/models.md](#srcappsauthenticationmodelsmd)
- [src/apps/authentication/serializers.md](#srcappsauthenticationserializersmd)
- [src/apps/authentication/services.md](#srcappsauthenticationservicesmd)
- [src/apps/authentication/tests/README.md](#srcappsauthenticationtestsreadmemd)
- [src/apps/authentication/tests/helpers.md](#srcappsauthenticationtestshelpersmd)
- [src/apps/authentication/tests/test_me.md](#srcappsauthenticationteststest_memd)
- [src/apps/authentication/tests/test_register.md](#srcappsauthenticationteststest_registermd)
- [src/apps/authentication/tests/test_tokens.md](#srcappsauthenticationteststest_tokensmd)
- [src/apps/authentication/urls.md](#srcappsauthenticationurlsmd)
- [src/apps/authentication/views.md](#srcappsauthenticationviewsmd)
- [src/apps/common/README.md](#srcappscommonreadmemd)
- [src/apps/common/apps.md](#srcappscommonappsmd)
- [src/apps/common/exceptions.md](#srcappscommonexceptionsmd)
- [src/apps/common/models.md](#srcappscommonmodelsmd)
- [src/apps/conftest.md](#srcappsconftestmd)
- [src/apps/customer/README.md](#srcappscustomerreadmemd)
- [src/apps/customer/admin.md](#srcappscustomeradminmd)
- [src/apps/customer/apps.md](#srcappscustomerappsmd)
- [src/apps/customer/models.md](#srcappscustomermodelsmd)
- [src/apps/customer/serializers.md](#srcappscustomerserializersmd)
- [src/apps/customer/services.md](#srcappscustomerservicesmd)
- [src/apps/customer/tests/README.md](#srcappscustomertestsreadmemd)
- [src/apps/customer/tests/helpers.md](#srcappscustomertestshelpersmd)
- [src/apps/customer/tests/test_services.md](#srcappscustomerteststest_servicesmd)
- [src/apps/customer/tests/test_views.md](#srcappscustomerteststest_viewsmd)
- [src/apps/customer/urls.md](#srcappscustomerurlsmd)
- [src/apps/customer/views.md](#srcappscustomerviewsmd)
- [src/core/README.md](#srccorereadmemd)
- [src/core/__init__.md](#srccore__init__md)
- [src/core/asgi.md](#srccoreasgimd)
- [src/core/celery.md](#srccorecelerymd)
- [src/core/settings/README.md](#srccoresettingsreadmemd)
- [src/core/settings/base.md](#srccoresettingsbasemd)
- [src/core/settings/celery.md](#srccoresettingscelerymd)
- [src/core/settings/channels.md](#srccoresettingschannelsmd)
- [src/core/settings/cors.md](#srccoresettingscorsmd)
- [src/core/settings/database.md](#srccoresettingsdatabasemd)
- [src/core/settings/email.md](#srccoresettingsemailmd)
- [src/core/settings/jwt.md](#srccoresettingsjwtmd)
- [src/core/settings/logging.md](#srccoresettingsloggingmd)
- [src/core/settings/openai.md](#srccoresettingsopenaimd)
- [src/core/settings/rest-framework.md](#srccoresettingsrest-frameworkmd)
- [src/core/settings/security.md](#srccoresettingssecuritymd)
- [src/core/settings/sentry.md](#srccoresettingssentrymd)
- [src/core/settings/storage.md](#srccoresettingsstoragemd)
- [src/core/urls.md](#srccoreurlsmd)
- [src/core/wsgi.md](#srccorewsgimd)
- [src/manage.md](#srcmanagemd)
- [tests/conftest.md](#testsconftestmd)
- [tests/test_healthcheck.md](#teststest_healthcheckmd)
- [scripts/beat.md](#scriptsbeatmd)
- [scripts/channels-worker.md](#scriptschannels-workermd)
- [scripts/channels.md](#scriptschannelsmd)
- [scripts/webserver.md](#scriptswebservermd)
- [scripts/worker.md](#scriptsworkermd)
- [.vscode/launch.md](#vscodelaunchmd)
- [.vscode/settings.md](#vscodesettingsmd)
- [recipes/README.md](#recipesreadmemd)
- [recipes/celery/README.md](#recipesceleryreadmemd)
- [recipes/celery/celery-beat.md](#recipescelerycelery-beatmd)
- [recipes/celery/celery-django.md](#recipescelerycelery-djangomd)
- [recipes/celery/celery-postgres-results.md](#recipescelerycelery-postgres-resultsmd)
- [recipes/celery/celery-redis-broker.md](#recipescelerycelery-redis-brokermd)
- [recipes/channels.md](#recipeschannelsmd)
- [recipes/chat.md](#recipeschatmd)
- [recipes/deployment.md](#recipesdeploymentmd)
- [recipes/openai-deep-agents.md](#recipesopenai-deep-agentsmd)
- [recipes/sentry/README.md](#recipessentryreadmemd)
- [recipes/sentry/sentry-django.md](#recipessentrysentry-djangomd)
- [recipes/sentry/sentry-python.md](#recipessentrysentry-pythonmd)
- [recipes/sse.md](#recipesssemd)
- [recipes/storage/storage-django.md](#recipesstoragestorage-djangomd)
- [recipes/storage/storage-s3-core.md](#recipesstoragestorage-s3-coremd)
- [recipes/tenancy.md](#recipestenancymd)
- [recipes/vector.md](#recipesvectormd)
- [source-map.md](#source-mapmd)

### README.md

#### Django Backend/API Standards

This repository is an English, Markdown-only handbook for building pragmatic Django backends and APIs. Markdown is the canonical source: complete fenced artifacts can be reconstructed into disposable, tested projects without committing generated code here.

The reference snapshot is Python 3.14.6, Django 6.0.7, and Django REST framework 3.17.1. Versions are intentionally frozen for the 2026-07-26 handbook snapshot; review upstream compatibility before advancing them.

##### Start here

- [Architecture](#docsarchitecturemd) explains boundaries and the two supported application styles.
- [Conventions](#docsconventionsmd) defines naming, services, selectors, typing, migrations, and dependency rules.
- [API design](#docsapi-designmd) covers JWT, error envelopes, request IDs, throttling, filtering, and cursor pagination.
- [Security](#docssecuritymd) covers tenant isolation, production validation, credentials, and upload controls.
- [Testing](#docstestingmd) defines the required test pyramid and acceptance matrix.
- [Operations](#docsoperationsmd) compares WSGI and ASGI deployment and describes health checks.
- [Reconstruction](#docsreconstructionmd) documents the artifact protocol and embeds the `reconstruct` utility.
- [Source map](#source-mapmd) accounts for all 91 files in the retired executable snapshot.
- [Base reference tree](#srcreadmemd) mirrors a generic Account/Customer API.
- [Recipes](#recipesreadmemd) — small composable modules for Celery, object storage, realtime delivery, vectors, optional AI, and Sentry.

##### Reconstruction

Extract the `reconstruct` artifact from [docs/reconstruction.md](#docsreconstructionmd) to a temporary executable, then run either a legacy alias:

```text
reconstruct --profile base|tasks|storage|realtime|vector-ai|full --output ABSOLUTE_PATH
```

or any explicit combination of the finer-grained modules documented in [recipes](#recipesreadmemd), mixed freely with aliases:

```text
reconstruct --modules celery-django,sentry-django,storage-s3-core --output ABSOLUTE_PATH
```

The destination must be an explicit, empty absolute directory. The utility rejects traversal, duplicate profile artifacts, malformed fences, and conflicting targets. It never writes generated files into this repository.

<!-- artifact: README.md; profiles: base -->
```markdown
# Generic Django Standard API

This derived teaching project demonstrates an account-scoped Django 6 and Django REST framework API. It contains email authentication, hardened JWT refresh rotation, layered API throttling, Customer CRUD, request IDs, error envelopes, health checks, admin, migrations, and tests.

The generated tree is disposable. Review the handbook standards and adapt the design deliberately before using it in a real service.

## Verify

~~~text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run coverage run -m pytest
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
~~~
```

##### Non-goals

This is not an active project generator, a framework layered over Django, or a production API contract. It does not prescribe repositories or use-case classes. Server-rendered templates and forms are outside scope.

##### Repository invariant

Every tracked file ends in `.md`. Files such as `pyproject.md`, `compose.md`, and `src/core/settings/base.md` are readable standards documents whose canonical fences reconstruct their executable counterparts.

### AGENTS.md

#### Repository Guidelines

##### Project Structure & Module Organization

This is a Markdown-only Django backend/API handbook. `docs/` defines cross-cutting architecture, API, security, testing, operations, and reconstruction standards. `src/core/` and `src/apps/` mirror the base Django reference project; their `.md` files contain complete canonical artifacts. `recipes/` adds optional tasks, storage, realtime, vector, AI, tenancy, and deployment profiles. Root documents describe tooling and infrastructure, while `tests/` and `scripts/` document reconstructed test and process files. Keep `source-map.md` aligned with all 91 paths from the retired executable repository.

##### Build, Test, and Development Commands

Extract the utility embedded in `docs/reconstruction.md`, then materialize a profile only into an empty directory outside this repository:

```text
reconstruct --profile base --output /tmp/django-standard-base
```

Inside a reconstructed `base` or `full` project, run:

```text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run coverage run -m pytest
uv run coverage report --fail-under=90
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
```

Before handoff, validate all six profiles as described in `docs/testing.md`, then run `git diff --check` and `git status --short`.

##### Coding Style & Naming Conventions

Every tracked file must end in `.md`. Use concise English, ATX headings, repository-relative links, and fenced languages matching artifact target types. Canonical markers must immediately precede one complete fence:

```markdown
&lt;!-- artifact: src/apps/customer/models.py; profiles: base,full --&gt;
```

Never use ellipses in canonical code. Prefer direct Django/DRF CRUD; use services for transactions or effects and selectors for reusable complex reads. Do not introduce repository or use-case layers.

##### Cross-App Boundaries

Every app under `src/apps/` owns its models privately. When one app's functionality is consumed by another app (for example, an AI/assistant app calling into a domain app's data), apply these rules to every new artifact:

- Define a `dtos.py` in the owning app with `pydantic.BaseModel` classes for any function whose parameters or return value would otherwise be a model instance, a queryset, or more than two or three plain parameters. Prefer one DTO parameter over a long keyword-argument list.
- A service or selector meant to be called from another app returns DTOs, never a model instance or `QuerySet`. Same-app callers (a ViewSet, a serializer, a test in that app) may still use the app's own models and querysets directly; the DTO boundary applies at the point another app imports from this one.
- The consuming app imports only `dtos.py` and the specific service/selector functions it needs (e.g. `from apps.<owner>.dtos import WidgetDTO` and `from apps.<owner>.services import list_widgets`). It must never import `models.py`, build a `QuerySet`, or otherwise reach into another app's internals.
- Name a cross-app read entry point after what it returns (e.g. `list_widgets`), not after its storage shape, and keep it in the owning app's `services.py` or `selectors.py`.
- This rule governs the shape of any new cross-app artifact; it does not itself require adding a new domain app. `customer` remains the handbook's only CRUD teaching app.

##### Testing Guidelines

Use pytest with files named `test_*.py` in reconstructed projects. Maintain at least 90% coverage for `base` and `full`. Follow Arrange, Act, Assert in that order; treat `pytest.raises` as an assertion and establish all inputs before it. Test tenant isolation, authorization failures, migrations, health checks, and each affected recipe. Avoid tests that only restate framework behavior, settings, route registration, or internal call shapes. Use deterministic mocks for vendor APIs; never require real credentials.

##### Commit & Pull Request Guidelines

History follows Conventional Commit prefixes such as `feat:` and `chore:` with short imperative summaries. Keep commits focused. Pull requests should explain the standard changed, affected profiles, reconstruction results, and security or migration implications; link relevant issues and include rendered-document screenshots only when formatting materially changes.

##### Security & Agent Instructions

Never commit secrets, reconstructed output, generated code, or product-specific data. Scope every account-owned query before lookup or mutation. Do not run destructive database, bucket, or worktree commands without explicit authorization.

##### Knowledge Graph

This repository has a graphify knowledge graph in `graphify-out/`. Before exploring the codebase manually for an architecture, cross-file, or "how does X relate to Y" question, query it first:

```text
graphify query "<question>"
```

Fall back to manual exploration only if the graph doesn't have an answer. After adding, removing, or materially changing `.md` files, run `/graphify --update` to keep the graph in sync.

### docs/api-design.md

#### API Design

##### Purpose and when to use it

Use these defaults for authenticated JSON REST APIs.

##### Responsibilities and invariants

JWT access tokens are short lived. Refresh tokens rotate and old refresh tokens are blacklisted. Registration never logs secrets and returns the same public user shape as `/auth/me/`.

Errors use one envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": {"email": ["Enter a valid email address."]},
    "request_id": "01J2N8Y5Q7M6R4T3V1W0X9Z8AB"
  }
}
```

The request ID is accepted only when syntactically safe; otherwise middleware generates one. It is returned in `X-Request-ID`, logged, and included in handled error responses.

Customer list endpoints support `search`, a small allowlist of ordering fields, and cursor pagination ordered by `-created_at,-id`. The unique tie-breaker is mandatory. Querysets are account-scoped before filtering.

##### Throttling and rate limits

Apply rate limits in layers:

- `AnonRateThrottle` bounds unauthenticated traffic by DRF's client identifier.
- `UserRateThrottle` provides a sustained per-user limit and falls back to the
  client identifier before authentication.
- `BurstRateThrottle` uses a separate scope for short spikes.
- `ScopedRateThrottle` adds tighter limits to registration, token, refresh,
  verification, and resource-heavy endpoints through `throttle_scope`.

Every configured class is evaluated, so the strictest applicable limit wins.
Views that set `throttle_classes` replace the global list; prefer a
`throttle_scope` when the endpoint should retain global limits. Health probes
are the deliberate exception and set `throttle_classes = ()`.

Treat a DRF 429 response and its `Retry-After` header as part of the API
contract. Clients must use bounded exponential backoff with jitter and must not
retry non-idempotent requests blindly.

DRF throttles use Django's cache and non-atomic cache operations. Local-memory
caches count separately per worker and small request overruns are possible
under concurrency. Use a shared production cache, monitor 429 volume by scope,
and enforce denial-of-service, credential-stuffing, and volumetric controls at
the trusted edge. Configure DRF's `NUM_PROXIES` only for a fixed, trusted proxy
topology that strips spoofed forwarding headers; otherwise use the direct
remote address.

With Django's Redis cache backend and the `redis` package installed, the
production cache setting has this shape:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "TIMEOUT": 300,
    }
}
```

Keep local tests on `LocMemCache` unless they explicitly prove shared-cache
behavior. Never use Django's database cache as a high-traffic throttle store.

`/health/live/` only reports process liveness. `/health/ready/` verifies required dependencies and returns 503 when unavailable. Health responses disclose no credentials or internal exception details.

##### Alternatives and trade-offs

Session authentication remains appropriate for same-origin browser applications. Page-number pagination is easier to navigate but is less stable under concurrent writes. Application throttling is intentionally approximate; exact quotas require an atomic quota service and a product-specific usage model.

##### Required tests

Cover token rotation/revocation, unauthenticated denial, malformed input, stable cursors, request IDs, error envelopes, cross-account denial, isolated throttle identities, scoped 429 responses, `Retry-After`, and health-probe bypass.

### docs/architecture.md

#### Architecture

##### Purpose and when to use it

Use this standard for JSON Django backends that benefit from Django's ORM, admin, migrations, authentication, and DRF.

##### When not to use it

Do not adopt Django for a tiny stateless function, a primarily server-rendered application covered by another standard, or a workload whose dominant constraint requires a different runtime.

##### Responsibilities and invariants

The base project has `core` for process configuration and `apps` for application behavior. `authentication` owns the email user, `account` owns tenancy, `customer` demonstrates CRUD, `api` owns HTTP-wide policy, and `common` holds genuinely shared Django primitives.

Simple CRUD stays in models, serializers, and ViewSets. A service is justified by a transaction, multiple writes, or an external effect. A selector is justified by a reusable complex read. Neither hides the ORM. Repository and use-case layers are deliberately excluded.

Account isolation is structural: every tenant-owned model inherits `AccountOwnedModel`, and every endpoint scopes its queryset before object lookup. Base tenancy is one Account per User. Advanced membership and account selection are optional recipes.

##### Alternatives and trade-offs

A single settings package, split by concern rather than by environment, avoids drift among environment-specific settings files, at the cost of explicit environment parsing and fail-fast production validation. Cursor pagination provides stable traversal but does not expose arbitrary page numbers.

##### Required tests

Test models, direct CRUD, services, selectors, permissions, tenant isolation, migrations, and configuration checks independently.

##### Related standards

See [conventions](#docsconventionsmd), [API design](#docsapi-designmd), [view patterns](#docsview-patternsmd), and the [base reference tree](#srcreadmemd).

### docs/conventions.md

#### Conventions

##### Purpose and when to use it

These conventions keep ordinary Django code explicit and reviewable.

##### Responsibilities and invariants

- Models declare fields and relations; they do not carry business-rule validation.
- Serializers validate and represent API data; they do not orchestrate side effects. Cross-field and business-rule validation belongs here, not on the model.
- ViewSets authorize, scope, validate, and delegate; see [view patterns](#docsview-patternsmd) for choosing between `ModelViewSet`, `GenericViewSet` with mixins, and plain `APIView`.
- Services accept keyword-only inputs and own transactions or effects.
- Selectors return typed QuerySets and own reusable read composition for same-app callers. A service or selector consumed by another app returns Pydantic DTOs from that app's `dtos.py` instead; the consuming app imports only DTOs and functions, never models or querysets, from the app it depends on.
- Migrations are committed, forward-only history; never edit an applied migration.
- URLs use stable nouns and trailing slashes.
- Timestamps are UTC and generated with timezone-aware APIs.
- Logs are structured and must not contain access tokens, passwords, file contents, or provider prompts.

Ruff formats and lints. `ty` checks useful Python surfaces, but Django's dynamic model fields, managers, reverse relations, and some DRF generics remain imperfectly modeled. Prefer a narrow line-level suppression with a reason plus runtime tests; blanket package or project ignores are prohibited.

##### Anti-patterns to avoid

Do not use `CheckConstraint` or a model `clean()` override to validate business rules such as "exactly one of these fields must be set." These are database/model-level mechanisms that duplicate logic which belongs in the serializer and produce harder-to-read errors for API consumers.

Avoid this:

```python
class TransactionLink(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="link")
    expense = models.ForeignKey("expenses.Expense", on_delete=models.CASCADE, null=True, blank=True)
    installment = models.ForeignKey("payments.Installment", on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey("expenses.Payment", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints: ClassVar[list] = [
            models.CheckConstraint(
                condition=(
                    Q(expense__isnull=False, installment__isnull=True, payment__isnull=True)
                    | Q(expense__isnull=True, installment__isnull=False, payment__isnull=True)
                    | Q(expense__isnull=True, installment__isnull=True, payment__isnull=False)
                ),
                name="ck_transaction_links_exactly_one_target",
            ),
        ]
```

Avoid this too:

```python
class TransactionLink(models.Model):
    ...

    def clean(self) -> None:
        super().clean()
        errors = {}
        target_ids = [self.expense_id, self.installment_id, self.payment_id]
        if len([target_id for target_id in target_ids if target_id is not None]) != 1:
            errors["non_field_errors"] = "A transaction link must have exactly one target."
        if self.expense_id is not None and self.expense.type == ExpenseType.INSTALLMENT:
            errors["expense"] = "Installment expenses must be linked through an installment."
        if self.expense_id is not None and self.expense.type == ExpenseType.RECURRENT:
            errors["expense"] = "Recurrent expenses must be linked through a payment."
        if self.payment_id is not None and self.payment.expense.type != ExpenseType.RECURRENT:
            errors["payment"] = "Only recurring payments can be linked to a transaction."
        if errors:
            raise ValidationError(errors)
```

Put this validation in the serializer's `validate()` instead. Only use `CheckConstraint` or `full_clean()`/`clean()` when explicitly requested, and write them deliberately rather than by default.

Do this instead — the model declares fields only:

```python
class TransactionLink(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="link")
    expense = models.ForeignKey("expenses.Expense", on_delete=models.CASCADE, null=True, blank=True)
    installment = models.ForeignKey("payments.Installment", on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey("expenses.Payment", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "transaction_links"
```

And the serializer owns the validation:

```python
class TransactionLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLink
        fields = ["id", "transaction", "expense", "installment", "payment"]

    def validate(self, attrs):
        targets = [attrs.get("expense"), attrs.get("installment"), attrs.get("payment")]
        if len([target for target in targets if target is not None]) != 1:
            raise serializers.ValidationError("A transaction link must have exactly one target.")

        expense = attrs.get("expense")
        if expense is not None and expense.type == ExpenseType.INSTALLMENT:
            raise serializers.ValidationError({"expense": "Installment expenses must be linked through an installment."})
        if expense is not None and expense.type == ExpenseType.RECURRENT:
            raise serializers.ValidationError({"expense": "Recurrent expenses must be linked through a payment."})

        payment = attrs.get("payment")
        if payment is not None and payment.expense.type != ExpenseType.RECURRENT:
            raise serializers.ValidationError({"payment": "Only recurring payments can be linked to a transaction."})

        return attrs
```

##### Alternatives and trade-offs

Direct ORM code is preferred until query reuse or complexity is demonstrated. A selector is not a generic data-access layer. A service is not required merely to call `Model.objects.create()`.

##### Required tests

Run Ruff, `ty`, pytest, coverage, Django checks, and migration drift checks. See [testing](#docstestingmd).

### docs/operations.md

#### Operations

##### Purpose and when to use it

Use these deployment patterns after selecting the capabilities the service actually needs.

##### WSGI and ASGI

Gunicorn with `core.wsgi` is the conservative default for synchronous REST. It has simple worker behavior and broad operational familiarity.

Daphne with `core.asgi` is required for long-lived async SSE and WebSockets. Channels routes HTTP and WebSocket protocols through `ProtocolTypeRouter`; Redis is the production channel layer. A reverse proxy may route ordinary REST to Gunicorn and realtime paths to Daphne, or Daphne may serve both.

Do not run blocking ORM or network work directly on an event loop. Use Django's async-safe interfaces or explicit sync adapters. Never set `DJANGO_ALLOW_ASYNC_UNSAFE` in production.

##### Deployment invariants

- Run migrations once as a release job, not concurrently in every web worker.
- When Celery beat is deployed, run `sync_periodic_tasks` in that same release
  job so the database-backed schedule reflects code before beat starts.
- Serve static assets outside application workers.
- Terminate TLS at a trusted proxy and configure forwarded-proto handling.
- Use liveness for process restarts and readiness for traffic admission.
- Gracefully drain workers; reconnecting SSE and WebSocket clients resume from event IDs or application state.
- Send structured JSON logs to stdout and initialize Sentry only when a DSN is configured.

##### Required tests

Validate container configuration, production settings, graceful shutdown, health endpoints, migration drift, and one smoke request through the chosen process server.

### docs/reconstruction.md

#### Reconstruction

##### Purpose and when to use it

Use `reconstruct` to materialize one disposable, executable reference project
from the canonical artifacts in this handbook. Run it from the repository
root and send the output to a fresh directory outside the repository.

Content is organized as small, independently selectable **modules** with
explicit dependency edges (`requires`). Request any combination of modules
and `reconstruct` resolves the transitive closure automatically. The six
names used before this handbook adopted modules — `base`, `tasks`,
`storage`, `realtime`, `vector-ai`, `full` — still work, as **aliases** that
expand to a fixed module set:

| Module family | Members | Notes |
| --- | --- | --- |
| Sentry | `sentry-python`, `sentry-django` | `sentry-django` requires `sentry-python` |
| Celery | `celery-core`, `celery-redis-broker`, `celery-postgres-results`, `celery-django`, `celery-beat` | see requirement chain below |
| Storage | `storage-s3-core`, `storage-django` | `storage-django` requires `storage-s3-core` |
| Realtime | `realtime-sse`, `realtime-channels` | independent of each other |
| Vector/AI | `vector-pgvector`, `vector-ai-openai`, `chat-streaming` | `vector-ai-openai` requires `vector-pgvector`; `chat-streaming` requires `celery-core`, `celery-redis-broker`, `realtime-sse` (it has its own task and Redis client, independent of the `apps.jobs` Job model) |
| Tenancy | `tenancy-advanced` | independent |

Celery requirement chain: `celery-redis-broker` and `celery-postgres-results`
both require only `celery-core`; `celery-django` (the durable `Job` model's
task glue) requires `celery-core` **and** `celery-postgres-results`, because
its tasks and services operate on the `Job` model that
`celery-postgres-results` owns; `celery-beat` requires `celery-django`.

| Alias | Resolves to |
| --- | --- |
| `base` | no modules — the generic Django REST API, account tenancy, authentication, and Customer CRUD that every request always includes |
| `tasks` | `celery-core`, `celery-django`, `celery-redis-broker`, `celery-postgres-results`, `celery-beat` |
| `storage` | `storage-s3-core`, `storage-django` |
| `realtime` | `realtime-sse`, `realtime-channels` |
| `vector-ai` | `vector-pgvector`, `vector-ai-openai`, `chat-streaming` |
| `full` | every module listed above, plus `sentry-django` and `tenancy-advanced` |

`base` content is inherited by every request, module or alias, exactly as
before.

##### When not to use it

Do not use reconstruction as an application generator or write its result
back into this handbook. A reconstructed tree is a derived test fixture, not
another canonical source. Fork the resulting design deliberately in a real
project rather than repeatedly regenerating an application that has begun to
evolve.

##### Responsibilities and invariants

A canonical artifact consists of one marker immediately followed by one
fenced block:

````markdown
&lt;!-- artifact: src/apps/customer/models.py; profiles: base,full --&gt;
```python
complete_file_contents = True
```
````

The target is a repository-relative POSIX path. The `profiles:` list is an
order-independent set of module names and/or alias names (see the tables
above); `dependency-fragment` markers use a `modules:` list restricted to
plain module names (aliases are not meaningful there — a fragment activates
per resolved module, and an alias only ever appears expanded). A
target/profile pair may occur only once across the entire handbook, exactly
as before. The fence language must agree with the target type.

`base` is inherited by every request. Artifacts explicitly assigned to a
requested module or alias replace a base artifact at the same exact target.
Recipe artifacts that belong in the combined project therefore declare both
their module tag and `full`. A combined aggregator, such as `settings.py`,
can declare a dedicated `full` variant. Whether an artifact applies to a
request is decided by intersecting the artifact's own tags against the union
of two sets: the modules the request transitively resolves to (plain module
names only — aliases never appear here), and the request's own literal
tags as typed (which may still be an alias). This is why a request only
closes over module `requires` edges, never over an artifact's alias tags: an
artifact tagged `celery-beat,tasks,full` applies to `--modules celery-beat`
(direct tag match) and to `--profile tasks` (`celery-beat` is one of the
modules `tasks` resolves to) and to `--profile full` (`full` is a literal
tag on the artifact and the literal request), but *not* to
`--modules celery-django` alone, since neither `celery-beat` nor `tasks` nor
`full` is in that request's resolved or literal set.

###### Dependency fragments

`pyproject.toml`'s dependency list cannot be owned by one profile-specific
whole-file artifact the way most files are — with modules composable, there
is no fixed number of dependency combinations to pre-bake. Instead
`pyproject.toml` has exactly one `base` **artifact** (project metadata, tool
configuration, and a `dependencies = [...]` array containing a placeholder
line `    # {{FRAGMENT:dependencies}}`), plus any number of small
**dependency-fragment** markers that each contribute the array entries one
module introduces:

````markdown
&lt;!-- dependency-fragment: pyproject.toml#dependencies; modules: sentry-python --&gt;
```toml
    "sentry-sdk[django]==2.66.1",
```
````

At materialization time, every fragment whose `modules:` tag is in the
resolved module set is concatenated (sorted by module name, then by
document/line for determinism) and substituted for the placeholder line, so
the emitted `pyproject.toml` has exactly the dependencies its resolved
module set introduces — no unused entries. A fragment for a module absent
from the request contributes nothing. Two selected fragments with
byte-identical content (e.g. two modules that both need the same
`tool.pytest.ini_options` line) collapse to one copy in the output, so a
config line shared by more than one module can be declared once per owning
module without producing a duplicate.

The utility performs all repository, marker, fence, profile, fragment, path,
language, and selected-tree conflict validation before its first write. The
output must be an existing, empty, absolute directory outside the
repository, with no symbolic-link component. The utility never deletes or
overwrites a path.

##### Migration generation

An ordinary schema migration only replays what `makemigrations` would
already derive from its app's `models.py`. Carrying it as a canonical
artifact would duplicate the models it comes from, so `account`,
`authentication`, `common`, `customer`, and the plain recipe apps (`files`,
`jobs`, `membership`, `realtime`) ship no migration artifacts. After
materializing a project, run:

```bash
uv run python src/manage.py makemigrations account authentication common customer
```

adding any plain recipe app included in the resolved module set. Commit the
generated migrations in the derived project; they become that project's own
forward-only history per [conventions](#docsconventionsmd).

A migration stays a canonical artifact only when it carries logic
`makemigrations` cannot derive from models alone: enabling a database
extension, a data migration, or a hand-written index.
`src/apps/documents/migrations/0001_initial.py` in
[pgvector](#recipesvectormd) is the sample — it mixes ordinary
`CreateModel` operations with `VectorExtension()` and a `RunPython`/`RunSQL`
HNSW index pair, so it must be authored once and reconstructed exactly, not
regenerated.

##### Dependency lock generation

Because modules are freely composable, pre-baking a `uv.lock` for every
possible combination is not attempted — the same reasoning as migrations
above. After materializing a project and (if needed) running
`makemigrations`, run:

```bash
uv lock
```

once, from the materialized project root, to produce the lock file for the
exact module set just generated. Commit it in the derived project alongside
the generated migrations.

##### Complete reconstruction utility

The utility uses only the Python standard library. Its marker is
intentionally `utility`, not `artifact`: the executable belongs beside a
temporary reconstruction, not inside every reconstructed Django project.

<!-- utility: reconstruct; language: python -->
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import stat
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MODULES: dict[str, frozenset[str]] = {
    "sentry-python": frozenset(),
    "sentry-django": frozenset({"sentry-python"}),
    "celery-core": frozenset(),
    "celery-redis-broker": frozenset({"celery-core"}),
    "celery-postgres-results": frozenset({"celery-core"}),
    "celery-django": frozenset({"celery-core", "celery-postgres-results"}),
    "celery-beat": frozenset({"celery-django"}),
    "storage-s3-core": frozenset(),
    "storage-django": frozenset({"storage-s3-core"}),
    "realtime-sse": frozenset(),
    "realtime-channels": frozenset(),
    "vector-pgvector": frozenset(),
    "vector-ai-openai": frozenset({"vector-pgvector"}),
    "chat-streaming": frozenset({"celery-core", "celery-redis-broker", "realtime-sse"}),
    "tenancy-advanced": frozenset(),
}

ALIAS_MEMBERS: dict[str, frozenset[str]] = {
    "base": frozenset(),
    "tasks": frozenset(
        {
            "celery-core",
            "celery-django",
            "celery-redis-broker",
            "celery-postgres-results",
            "celery-beat",
        }
    ),
    "storage": frozenset({"storage-s3-core", "storage-django"}),
    "realtime": frozenset({"realtime-sse", "realtime-channels"}),
    "vector-ai": frozenset({"vector-pgvector", "vector-ai-openai", "chat-streaming"}),
    "full": frozenset(MODULES) | frozenset({"sentry-django", "tenancy-advanced"}),
}

TAG_SET = frozenset(MODULES) | frozenset(ALIAS_MEMBERS)

MARKER_RE = re.compile(
    r"^<!-- artifact: (?P<target>[^;]+); profiles: (?P<profiles>[^>]+) -->\r?\n?$"
)
FRAGMENT_RE = re.compile(
    r"^<!-- dependency-fragment: (?P<target>[^#]+)#(?P<section>[^;]+); "
    r"modules: (?P<modules>[^>]+) -->\r?\n?$"
)
FENCE_RE = re.compile(r"^```(?P<language>[A-Za-z0-9_+.-]+)\r?\n?$")
ORDINARY_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)\r?\n?$")
PLACEHOLDER_RE = re.compile(r"^(?P<indent>[ \t]*)# \{\{FRAGMENT:(?P<section>[A-Za-z0-9_-]+)\}\}\r?\n?$")

EXACT_LANGUAGES = {
    ".gitignore": frozenset({"gitignore", "text"}),
    ".python-version": frozenset({"text"}),
    "Dockerfile": frozenset({"dockerfile"}),
    "Makefile": frozenset({"makefile"}),
}
SUFFIX_LANGUAGES = {
    ".conf": frozenset({"text"}),
    ".ini": frozenset({"ini"}),
    ".json": frozenset({"json"}),
    ".lock": frozenset({"toml"}),
    ".md": frozenset({"markdown"}),
    ".py": frozenset({"python"}),
    ".pyi": frozenset({"python"}),
    ".sh": frozenset({"bash", "sh"}),
    ".toml": frozenset({"toml"}),
    ".txt": frozenset({"text"}),
    ".yaml": frozenset({"yaml"}),
    ".yml": frozenset({"yaml"}),
}


class ReconstructionError(Exception):
    """A user-correctable repository or destination error."""


@dataclass(frozen=True)
class Artifact:
    target: PurePosixPath
    profiles: Sequence[str]
    language: str
    content: str
    document: str
    line: int


@dataclass(frozen=True)
class Fragment:
    target: PurePosixPath
    section: str
    modules: Sequence[str]
    content: str
    document: str
    line: int


def _close_modules(requested: frozenset[str]) -> frozenset[str]:
    unknown = sorted(requested - TAG_SET)
    if unknown:
        raise ReconstructionError(f"unknown modules: {', '.join(unknown)}")
    expanded: set[str] = set()
    for item in requested:
        expanded |= ALIAS_MEMBERS.get(item, frozenset({item}))
    frontier = set(expanded)
    while frontier:
        additions: set[str] = set()
        for module in frontier:
            additions |= MODULES.get(module, frozenset()) - expanded
        expanded |= additions
        frontier = additions
    return frozenset(expanded)


def resolve_modules(requested: frozenset[str]) -> frozenset[str]:
    if not requested:
        raise ReconstructionError("at least one module or alias is required")
    return _close_modules(requested)


def run_git(repo: Path, *arguments: str) -> bytes:
    process = subprocess.run(
        ("git", *arguments),
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise ReconstructionError(f"git {' '.join(arguments)} failed: {detail}")
    return process.stdout


def repository_root() -> Path:
    try:
        raw_root = subprocess.run(
            ("git", "rev-parse", "--show-toplevel"),
            cwd=Path.cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as error:
        raise ReconstructionError("git is required to locate tracked Markdown") from error
    if raw_root.returncode != 0:
        raise ReconstructionError("run reconstruct from a Git repository root")
    root = Path(raw_root.stdout.decode("utf-8").strip()).resolve()
    if Path.cwd().resolve() != root:
        raise ReconstructionError(f"run reconstruct from the repository root: {root}")
    return root


def tracked_markdown(repo: Path) -> list[Path]:
    entries = run_git(repo, "ls-files", "-z").split(b"\0")
    names = [entry.decode("utf-8") for entry in entries if entry]
    non_markdown = [name for name in names if not name.endswith(".md")]
    if non_markdown:
        sample = ", ".join(non_markdown[:5])
        raise ReconstructionError(f"tracked paths must all end in .md: {sample}")
    paths: list[Path] = []
    for name in names:
        candidate = repo / name
        if not candidate.is_file():
            raise ReconstructionError(f"tracked Markdown is missing from the worktree: {name}")
        paths.append(candidate)
    return sorted(paths)


def safe_target(raw_target: str, document: str, line: int) -> PurePosixPath:
    if raw_target != raw_target.strip() or not raw_target:
        raise ReconstructionError(f"{document}:{line}: target has surrounding whitespace")
    if "\\" in raw_target or "\0" in raw_target or raw_target.startswith("/"):
        raise ReconstructionError(f"{document}:{line}: target is not a safe POSIX path")
    raw_parts = raw_target.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ReconstructionError(f"{document}:{line}: target contains an unsafe component")
    if any(":" in part or any(ord(character) < 32 for character in part) for part in raw_parts):
        raise ReconstructionError(f"{document}:{line}: target contains unsafe characters")
    target = PurePosixPath(raw_target)
    if target.is_absolute():
        raise ReconstructionError(f"{document}:{line}: target must be relative")
    return target


def allowed_languages(target: PurePosixPath) -> frozenset[str]:
    if target.name in EXACT_LANGUAGES:
        return EXACT_LANGUAGES[target.name]
    if target.name.startswith(".env"):
        return frozenset({"dotenv"})
    allowed = SUFFIX_LANGUAGES.get(target.suffix.lower())
    if allowed is None:
        raise ReconstructionError(f"unsupported artifact target type: {target}")
    return allowed


def closing_fence(line: str, opening: str) -> bool:
    stripped = line.rstrip("\r\n")
    if not stripped or stripped[0] != opening[0]:
        return False
    return not stripped.strip(opening[0]).strip() and len(stripped) >= len(opening)


def _parse_tag_list(raw: str, document: str, line: int, kind: str) -> tuple[str, ...]:
    items = tuple(item.strip() for item in raw.split(","))
    if not items or any(not item for item in items) or len(set(items)) != len(items):
        raise ReconstructionError(f"{document}:{line}: {kind} must be a unique non-empty list")
    unknown = sorted(set(items) - TAG_SET)
    if unknown:
        raise ReconstructionError(f"{document}:{line}: unknown {kind}: {', '.join(unknown)}")
    return items


def _read_fence(
    lines: list[str], index: int, target: PurePosixPath, document: str, marker_line: int
) -> tuple[str, str, int]:
    if index + 1 >= len(lines):
        raise ReconstructionError(f"{document}:{marker_line}: marker has no fenced artifact")
    opening = FENCE_RE.fullmatch(lines[index + 1])
    if opening is None:
        raise ReconstructionError(
            f"{document}:{marker_line}: marker must be immediately followed "
            "by a named triple-backtick fence"
        )
    language = opening.group("language").lower()
    allowed = allowed_languages(target)
    if language not in allowed:
        expected = ", ".join(sorted(allowed))
        raise ReconstructionError(
            f"{document}:{marker_line}: {target} requires fence language {expected}, "
            f"not {language}"
        )
    close_index = index + 2
    while close_index < len(lines):
        if lines[close_index].rstrip("\r\n") == "```":
            break
        close_index += 1
    if close_index == len(lines):
        raise ReconstructionError(f"{document}:{marker_line}: canonical fence is not closed")
    content = "".join(lines[index + 2 : close_index])
    return content, language, close_index


def parse_document(
    repo: Path, document_path: Path
) -> tuple[list[Artifact], list[Fragment]]:
    relative = document_path.relative_to(repo).as_posix()
    text = document_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    artifacts: list[Artifact] = []
    fragments: list[Fragment] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        marker = MARKER_RE.fullmatch(line)
        fragment_marker = FRAGMENT_RE.fullmatch(line)
        if marker is not None:
            marker_line = index + 1
            target = safe_target(marker.group("target"), relative, marker_line)
            profile_items = _parse_tag_list(
                marker.group("profiles"), relative, marker_line, "profiles"
            )
            content, language, close_index = _read_fence(lines, index, target, relative, marker_line)
            artifacts.append(
                Artifact(
                    target=target,
                    profiles=profile_items,
                    language=language,
                    content=content,
                    document=relative,
                    line=marker_line,
                )
            )
            index = close_index + 1
            continue
        if fragment_marker is not None:
            marker_line = index + 1
            target = safe_target(fragment_marker.group("target"), relative, marker_line)
            section = fragment_marker.group("section").strip()
            module_items = _parse_tag_list(
                fragment_marker.group("modules"), relative, marker_line, "modules"
            )
            unaliased = [item for item in module_items if item not in ALIAS_MEMBERS]
            if len(unaliased) != len(module_items):
                raise ReconstructionError(
                    f"{relative}:{marker_line}: dependency-fragment modules must be "
                    "plain module names, not aliases"
                )
            content, _language, close_index = _read_fence(lines, index, target, relative, marker_line)
            fragments.append(
                Fragment(
                    target=target,
                    section=section,
                    modules=module_items,
                    content=content,
                    document=relative,
                    line=marker_line,
                )
            )
            index = close_index + 1
            continue
        if "<!-- artifact:" in line or "<!-- dependency-fragment:" in line:
            raise ReconstructionError(f"{relative}:{index + 1}: malformed marker")
        ordinary = ORDINARY_FENCE_RE.match(line)
        if ordinary is not None:
            opening_fence = ordinary.group("fence")
            index += 1
            while index < len(lines) and not closing_fence(lines[index], opening_fence):
                index += 1
            if index < len(lines):
                index += 1
            continue
        index += 1
    return artifacts, fragments


def collect_artifacts(repo: Path) -> tuple[list[Artifact], list[Fragment]]:
    artifacts: list[Artifact] = []
    fragments: list[Fragment] = []
    seen: dict[tuple[PurePosixPath, str], Artifact] = {}
    for document_path in tracked_markdown(repo):
        document_artifacts, document_fragments = parse_document(repo, document_path)
        for artifact in document_artifacts:
            for profile in artifact.profiles:
                key = (artifact.target, profile)
                previous = seen.get(key)
                if previous is not None:
                    raise ReconstructionError(
                        f"duplicate {artifact.target} for {profile}: "
                        f"{previous.document}:{previous.line} and "
                        f"{artifact.document}:{artifact.line}"
                    )
                seen[key] = artifact
            artifacts.append(artifact)
        fragments.extend(document_fragments)
    return artifacts, fragments


def selected_artifacts(
    artifacts: list[Artifact], requested: frozenset[str], resolved: frozenset[str]
) -> dict[PurePosixPath, Artifact]:
    # An artifact applies if one of its own tags is either a module the
    # request transitively resolved to (`resolved`, always plain module
    # names) or a tag the caller typed literally (`requested`, which may
    # still be an alias like "tasks" or "full"). Matching against `resolved`
    # alone would miss alias-tagged artifacts (aliases never appear in
    # `resolved`); closing the artifact's own alias tags instead of the
    # request's would wrongly expand "full" into every module regardless of
    # what was actually requested.
    applicable = requested | resolved
    selected: dict[PurePosixPath, Artifact] = {}
    for artifact in artifacts:
        if "base" in artifact.profiles:
            selected[artifact.target] = artifact
    for artifact in artifacts:
        if set(artifact.profiles) & applicable:
            selected[artifact.target] = artifact
    if not selected:
        raise ReconstructionError("resolved module set has no artifacts")
    return selected


def merge_fragments(
    selected: dict[PurePosixPath, Artifact],
    fragments: list[Fragment],
    resolved: frozenset[str],
) -> dict[PurePosixPath, Artifact]:
    by_target_section: dict[tuple[PurePosixPath, str], list[Fragment]] = {}
    for fragment in fragments:
        if any(module in resolved for module in fragment.modules):
            by_target_section.setdefault((fragment.target, fragment.section), []).append(
                fragment
            )
    if not by_target_section:
        return selected
    merged = dict(selected)
    for (target, section), matches in by_target_section.items():
        artifact = merged.get(target)
        if artifact is None:
            raise ReconstructionError(f"dependency-fragment target not selected: {target}")
        lines = artifact.content.splitlines(keepends=True)
        placeholder_index = None
        for line_index, line in enumerate(lines):
            found = PLACEHOLDER_RE.fullmatch(line)
            if found is not None and found.group("section") == section:
                placeholder_index = line_index
                break
        if placeholder_index is None:
            raise ReconstructionError(
                f"{artifact.document}:{artifact.line}: no placeholder for section {section}"
            )
        ordered = sorted(matches, key=lambda item: (item.modules, item.document, item.line))
        seen_content: set[str] = set()
        deduplicated = []
        for fragment in ordered:
            if fragment.content in seen_content:
                continue
            seen_content.add(fragment.content)
            deduplicated.append(fragment)
        replacement = "".join(fragment.content for fragment in deduplicated)
        lines[placeholder_index : placeholder_index + 1] = [replacement]
        merged[target] = Artifact(
            target=artifact.target,
            profiles=artifact.profiles,
            language=artifact.language,
            content="".join(lines),
            document=artifact.document,
            line=artifact.line,
        )
    return merged


def validate_tree(selected: dict[PurePosixPath, Artifact]) -> None:
    targets = sorted(selected, key=lambda item: item.as_posix())
    folded: dict[str, PurePosixPath] = {}
    target_set = set(targets)
    for target in targets:
        folded_name = target.as_posix().casefold()
        prior = folded.get(folded_name)
        if prior is not None and prior != target:
            raise ReconstructionError(f"case-insensitive target conflict: {prior} and {target}")
        folded[folded_name] = target
        for parent in target.parents:
            if parent == PurePosixPath("."):
                break
            if parent in target_set:
                raise ReconstructionError(f"file/directory target conflict: {parent} and {target}")


def reject_symlink_components(destination: Path) -> None:
    current = Path(destination.anchor)
    for component in destination.parts[1:]:
        current = current / component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            raise ReconstructionError(f"output directory does not exist: {destination}")
        if stat.S_ISLNK(mode):
            raise ReconstructionError(f"output path contains a symbolic link: {current}")


def output_directory(raw_output: str, repo: Path) -> Path:
    destination = Path(raw_output)
    if not destination.is_absolute():
        raise ReconstructionError("--output must be an absolute path")
    reject_symlink_components(destination)
    if not destination.is_dir():
        raise ReconstructionError(f"output is not a directory: {destination}")
    destination = destination.resolve(strict=True)
    try:
        destination.relative_to(repo)
    except ValueError:
        pass
    else:
        raise ReconstructionError("output must be outside the Markdown repository")
    if any(destination.iterdir()):
        raise ReconstructionError(f"output directory must be empty: {destination}")
    return destination


def executable(target: PurePosixPath) -> bool:
    return (
        target.suffix == ".sh"
        or target.name == "manage.py"
        or (bool(target.parts) and target.parts[0] == "bin")
    )


def materialize(destination: Path, selected: dict[PurePosixPath, Artifact]) -> None:
    for relative_target in sorted(selected, key=lambda item: item.as_posix()):
        artifact = selected[relative_target]
        target = destination.joinpath(*relative_target.parts)
        target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        mode = 0o755 if executable(relative_target) else 0o644
        descriptor = os.open(target, flags, mode)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(artifact.content.encode("utf-8"))
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        prog="reconstruct",
        description="Materialize a canonical Django handbook module selection.",
    )
    selector = argument_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument(
        "--modules", metavar="MODULE[,MODULE...]", help="comma-separated modules and/or aliases"
    )
    selector.add_argument(
        "--profile", choices=sorted(ALIAS_MEMBERS), help="legacy alias, equivalent to --modules NAME"
    )
    argument_parser.add_argument("--output", required=True, metavar="ABSOLUTE_PATH")
    return argument_parser


def main() -> int:
    arguments = parser().parse_args()
    requested_raw = arguments.profile if arguments.profile else arguments.modules
    try:
        requested = frozenset(item.strip() for item in requested_raw.split(","))
        repo = repository_root()
        resolved = resolve_modules(requested)
        artifacts, fragments = collect_artifacts(repo)
        selected = selected_artifacts(artifacts, requested, resolved)
        selected = merge_fragments(selected, fragments, resolved)
        validate_tree(selected)
        destination = output_directory(arguments.output, repo)
        materialize(destination, selected)
    except (OSError, UnicodeError, ReconstructionError) as error:
        print(f"reconstruct: error: {error}", file=sys.stderr)
        return 2
    print(f"materialized {len(selected)} artifacts for {sorted(requested)} at {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

##### Bootstrap extraction

Create a temporary executable without copying the utility by hand. This
extractor also uses only the standard library and refuses to overwrite its
destination:

```bash
reconstruct_dir="$(mktemp -d)"
python3 - "$PWD/docs/reconstruction.md" "$reconstruct_dir/reconstruct" <<'PY'
import os
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(keepends=True)
destination = Path(sys.argv[2])
marker = "<!-- utility: reconstruct; language: python -->\n"
matches = [index for index, line in enumerate(source) if line == marker]
if len(matches) != 1:
    raise SystemExit("expected exactly one reconstruct utility marker")
start = matches[0] + 1
if start >= len(source) or source[start] != "```python\n":
    raise SystemExit("utility marker is not followed by a Python fence")
end = start + 1
while end < len(source) and source[end].rstrip("\r\n") != "```":
    end += 1
if end == len(source):
    raise SystemExit("reconstruct utility fence is not closed")
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
descriptor = os.open(destination, flags, 0o755)
with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
    stream.writelines(source[start + 1 : end])
PY
```

Then create an empty destination and invoke the exact interface — either a
legacy alias:

```bash
output_dir="$(mktemp -d /tmp/django-standard-base.XXXXXX)"
"$reconstruct_dir/reconstruct" --profile base --output "$output_dir"
```

or an explicit module combination, mixing atomic modules and aliases freely:

```bash
output_dir="$(mktemp -d /tmp/django-standard-custom.XXXXXX)"
"$reconstruct_dir/reconstruct" --modules celery-django,sentry-django --output "$output_dir"
```

Use a new output directory for every request. Running the command again
against the same directory correctly fails because it is no longer empty.
After materializing, run `makemigrations` (see
[Migration generation](#migration-generation)) and `uv lock` (see
[Dependency lock generation](#dependency-lock-generation)).

##### Alternatives and trade-offs

Keeping the utility embedded preserves the Markdown-only repository contract
and makes the parser reviewable with the protocol it enforces. It does
require one bootstrap extraction step. A packaged generator would be more
convenient to install, but would introduce a second canonical source and
revive lifecycle work that this handbook intentionally retired.

A composable module graph costs more validation surface than the flat
profile enum it replaced (transitive resolution, dependency-fragment
merging, alias/module tag overlap), but it is what makes "Celery without
Beat" or "Sentry on its own" expressible at all. The flat six-profile design
this replaces treated every recipe as an indivisible unit; that was simpler
to implement but forced an all-or-nothing choice per recipe, which is the
problem this revision exists to fix. Dependency-fragment merging is
deliberately restricted to one placeholder substitution per section rather
than arbitrary text patching, so a fragment can only append array entries in
a documented, reviewable location.

##### Required tests

- Extract the utility and confirm it is executable.
- Materialize every legacy alias (`base`, `tasks`, `storage`, `realtime`,
  `vector-ai`, `full`) into separate fresh directories under `/tmp` and
  confirm each alias's file set matches its documented module expansion.
- Materialize at least two module combinations that were not expressible
  before this revision, e.g. `celery-django` alone (no beat, no
  postgres-results, but `celery-core` pulled in transitively) and
  `sentry-django,celery-redis-broker` (crossing two otherwise-unrelated
  families).
- Reject a relative output, a repository-internal output, a non-empty
  output, a missing output, and an output with a symbolic-link component.
- Reject malformed markers, unknown modules or aliases, repeated tags,
  duplicate target/profile pairs, unsafe paths, unsupported target
  extensions, mismatched fence languages, unclosed fences, and
  file/directory conflicts.
- Reject a `dependency-fragment` marker whose `modules:` list contains an
  alias, and one whose target has no matching placeholder.
- Confirm a request inherits base artifacts and replaces only an exact
  target explicitly assigned to one of its resolved modules.
- Confirm `pyproject.toml` for a resolved module set contains exactly the
  dependency-fragment entries for that set, in deterministic order, with no
  duplicates and no entries from unselected modules.
- Confirm scripts and `src/manage.py` are executable and ordinary files are
  not.
- Run the reconstructed project checks in [testing](#docstestingmd), including
  `uv lock` succeeding against the generated `pyproject.toml`.

##### Related standards

See [architecture](#docsarchitecturemd), [testing](#docstestingmd), the
[source map](#source-mapmd), and the [recipe index](#recipesreadmemd).

### docs/security.md

#### Security

##### Purpose and when to use it

Apply this checklist to every reconstructed profile and deployment.

##### Responsibilities and invariants

Production starts only with a non-placeholder `SECRET_KEY`, `DEBUG=false`, non-empty `ALLOWED_HOSTS`, an explicit database URL, and HTTPS-aware cookie/proxy settings. Run `manage.py check --deploy` in the release pipeline.

Tenant identity comes from authenticated server-side state, never from a request-body `account_id`. Scope before lookup so cross-account IDs produce the same not-found behavior as unknown IDs.

Application throttling limits routine abuse and protects fair use, but is not a denial-of-service boundary. Use a shared cache across application workers, apply stricter scopes to authentication and expensive operations, and enforce authoritative limits at the trusted proxy or API gateway. Trust forwarded client addresses only when the proxy strips inbound forwarding headers and direct application access is blocked.

Credentials are environment variables. The canonical `.env.example` contains placeholders only. Rotate leaked credentials rather than merely deleting them from Git.

Private upload flows validate tenant ownership, object key prefix, declared size, observed size, and an allowlist of MIME types. Presigned operations are short lived. Provider callbacks and task delivery are idempotent.

OpenAI examples send `store=False` and a stable pseudonymous `safety_identifier`. They never expose provider errors verbatim and never use a real key in tests.

##### Required tests

Test production fail-fast behavior, deploy checks, JWT blacklisting, object-level isolation, throttle scopes and identity isolation, upload constraints, origin rejection, and secret scans.

### docs/testing.md

#### Testing and Acceptance

##### Repository validation

The Markdown validator must establish:

- every tracked path ends in `.md`;
- all 91 original paths appear exactly once in `source-map.md`;
- artifact paths are safe and markers have complete fenced blocks;
- artifact/profile pairs are unique;
- relative Markdown links resolve;
- forbidden secrets, generator commands, product-specific terms, unresolved placeholders, and incomplete canonical code are absent.

##### Reconstruction matrix

Materialize `base`, `tasks`, `storage`, `realtime`, `vector-ai`, and `full` into fresh directories under `/tmp`.

For `base` and `full`, run:

```text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run python src/manage.py makemigrations
uv run coverage run -m pytest
uv run coverage report --fail-under=90
uv run python src/manage.py check
uv run python src/manage.py check --deploy
uv run python src/manage.py makemigrations --check --dry-run
docker compose config
```

The plain apps ship no migration artifacts; see
[migration generation](#docsreconstructionmd). Run
`makemigrations` once before the drift check so it verifies the generated
migrations match the models, not that migrations are missing entirely.

Integration tests use PostgreSQL/pgvector, Redis, and MinIO. They cover JWT rotation/revocation, account isolation, direct CRUD, service and selector paths, task retries/idempotency, upload validation, vector isolation, ordered SSE with heartbeats and cancellation, WebSocket auth/origin/groups/reconnect, and a Daphne smoke test.

Test throttling only when an application's abuse model gives it a concrete
acceptance contract. Do not include generic tests that merely restate DRF's
throttling behavior or the settings dictionary.

OpenAI tests are deterministic mocks covering streaming text, refusal, rate
limiting, and provider failure. Test tool authorization, delegation,
persistence isolation, interrupts, and recovery through application behavior
when those capabilities are enabled. A real API key is neither required nor
used.

##### Test structure

Every test follows Arrange, Act, Assert in that order and labels the three
sections when the phases are not self-evident. Keep assertions after all actions
under test. Treat `pytest.raises` as an assertion: establish fixtures and inputs
first, then place the raising call inside the final Assert section. Split a test
when independent scenarios would require interleaving actions and assertions.

##### Final gate

Run `git diff --check`, inspect `git status --short`, and repeat the tracked Markdown-only invariant.

### docs/version-snapshot.md

#### Version Snapshot

The canonical pins were checked against current stable package indexes on 2026-07-26.

| Component | Version | Scope |
| --- | ---: | --- |
| Python | 3.14.6 | all profiles |
| Django | 6.0.7 | all profiles |
| Django REST framework | 3.17.1 | all profiles |
| Simple JWT | 5.5.1 | all profiles |
| django-filter | 26.1 | all profiles |
| psycopg | 3.3.4 | PostgreSQL |
| Ruff | 0.16.0 | development |
| ty | 0.0.63 | development |
| pytest | 9.1.1 | development |
| pre-commit | 4.6.1 | development |
| HTTPX | 0.28.1 | tasks and optional AI tests |
| Celery | 5.6.3 | tasks |
| Channels | 4.3.2 | realtime |
| Daphne | 4.2.3 | realtime |
| pgvector | 0.5.0 | vector |
| OpenAI Python | 2.48.0 | optional AI |
| Deep Agents | 0.6.12 | optional multi-step AI |
| LangChain OpenAI | 1.4.1 | Deep Agents OpenAI model adapter |
| websockets | 15.0.1 | realtime test compatibility |

Prereleases are excluded. A version bump must update `pyproject.md`, `uv-lock.md`, compatibility notes, and reconstructed verification together.

The handbook target is Python 3.14.6. At verification time, the available managed interpreter and official container patch were 3.14.4, so executable checks and the container artifact use 3.14.4 within the declared `>=3.14,<3.15` compatibility range. Advance the container pin to 3.14.6 after that official image is published and repeat every gate.

### docs/view-patterns.md

#### View Patterns

##### Purpose and when to use it

Django itself is never optional — there is no `django-views`,
`django-viewsets`, or `django-modelviewsets` module in
[reconstruction](#docsreconstructionmd)'s module graph. This standard instead
documents the three view-layer shapes already used across this handbook, so
the choice between them is explicit and discoverable rather than implicit
per app.

##### When not to use it

Do not reach for a heavier shape than the endpoint needs — see the decision
guide below before adding a `ModelViewSet` for a single custom action, or an
`APIView` for conventional CRUD that a `ModelViewSet` already gives you for
free.

##### Responsibilities and invariants

Three shapes cover every endpoint in this handbook:

- **`ModelViewSet`** (full CRUD): [`AccountScopedViewSet`](#srcappsapiviewsmd),
  the tenant-scoping base every full-CRUD resource inherits, subclasses
  `rest_framework.viewsets.ModelViewSet` directly. Use it when a resource
  needs list, retrieve, create, update, and destroy with no behavior beyond
  serializer and model operations plus account scoping — see
  [`CustomerViewSet`](#srcappscustomerviewsmd), which only overrides
  `perform_create` to attach the trusted account.
- **`GenericViewSet` + mixins** (partial CRUD): use when a resource exposes
  only some of the standard actions. [`JobViewSet`](#recipescelerycelery-postgres-resultsmd)
  combines `RetrieveModelMixin` with `GenericViewSet` because jobs are
  created by a service call from another endpoint, not by a client `POST`
  directly to the jobs resource — list/create/update/destroy would be
  meaningless there.
- **Plain `APIView`**: use for an endpoint that is not resource CRUD at all
  — a workflow step, a custom action shape, or a streaming response.
  [`StartUploadView`/`CompleteUploadView`/`DeleteFileView`](#recipesstoragestorage-djangomd)
  each model one step of a presigned-upload workflow, not a `StoredFile`
  CRUD resource. [`EventStreamView`](#recipesssemd) and
  [`ChatStartAPIView`](#recipeschatmd) use `APIView` because a
  `StreamingHttpResponse` and an async streaming body have no ViewSet
  action to map onto.

Every shape scopes its queryset (or, for plain `APIView`, its service call)
to the requesting account before any lookup — see
[architecture](#docsarchitecturemd)'s account-isolation invariant. No shape
hides the ORM: a service is justified by a transaction, multiple writes, or
an external effect, not by the choice of view class (see
[conventions](#docsconventionsmd)).

##### Alternatives and trade-offs

A hand-written `APIView` offers full control but repeats list, detail,
validation, and status-code behavior that ViewSets already make consistent
— reserve it for endpoints that genuinely are not resource CRUD.
`GenericViewSet` with explicit mixins costs one extra line per action
compared to `ModelViewSet`'s implicit "all five," in exchange for a
resource that cannot accidentally expose an action it never intended to
support.

##### Required tests

For a `ModelViewSet` or `GenericViewSet` resource, exercise every action it
exposes and confirm objects from another account are unreachable (404) for
retrieve, update, and destroy. For a plain `APIView`, test its specific
contract directly — there is no shared action matrix to inherit coverage
from.

##### Related standards

See [architecture](#docsarchitecturemd), [conventions](#docsconventionsmd),
[API design](#docsapi-designmd), [the account-scoped view base](#srcappsapiviewsmd),
and [testing](#docstestingmd).

### compose-dev.md

#### Local Infrastructure Compose

##### Purpose and when to use it

This development artifact runs PostgreSQL with pgvector, Redis, and private MinIO while Django runs on the host.

##### Complete canonical artifact

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

##### Responsibilities and invariants

Infrastructure ports bind only to loopback and credentials are required from the caller.

##### Required tests

Run `docker compose -f compose.dev.yaml config` and wait for health checks before integration tests.

### compose.md

#### Full-Profile Compose

##### Purpose and when to use it

This artifact is an integration environment for the reconstructed full profile, not a production orchestrator.

##### Complete canonical artifact

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

##### Responsibilities and invariants

Compose is for integration and demonstrations. Production uses managed secrets, durable services, TLS, backups, and an orchestrator.

##### Required tests

Run `docker compose config`, bring dependencies healthy, migrate once, and execute the integration suite.

### conftest.md

#### Root pytest Fixtures

##### Purpose and when to use it

This root fixture module supplies a stable password and API client helpers without creating tenant state implicitly.

##### When not to use it

Feature-specific objects belong in their application test helpers.

##### Complete canonical artifact

<!-- artifact: conftest.py; profiles: base -->
```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_password() -> str:
    return "correct-horse-battery-staple"
```

##### Required tests

Collect the suite with `pytest --collect-only`.

### dockerfile.md

#### Production Container

##### Purpose and when to use it

Use this multi-stage image for a reconstructed synchronous REST service.

##### When not to use it

Realtime deployments use the same image with the Daphne command documented by the realtime recipe.

##### Responsibilities and invariants

Dependencies are installed from the frozen lock, the process runs as an unprivileged user, and source is copied only after dependency installation.

##### Complete canonical artifact

<!-- artifact: Dockerfile; profiles: base -->
```dockerfile
FROM ghcr.io/astral-sh/uv:0.11.32 AS uv

FROM python:3.14.4-slim-bookworm AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14.4-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src /app/src
COPY --chown=app:app gunicorn.conf.py /app/gunicorn.conf.py
USER app
EXPOSE 8000
CMD ["gunicorn", "--chdir", "/app/src", "--config", "/app/gunicorn.conf.py", "core.wsgi:application"]
```

##### Alternatives and trade-offs

A distro-managed Python image is larger but easier to inspect than a distroless runtime.

##### Required tests

Build the image, run as the configured user, execute Django deploy checks, and smoke-test liveness.

##### Related standards

See [Gunicorn](#gunicornconfmd) and [operations](#docsoperationsmd).

### environment.md

#### Environment Variables

##### Purpose and when to use it

Copy the reconstructed `.env.example` to an untracked local file and replace placeholders. Production secrets belong in a secret manager.

##### When not to use it

Never commit a populated environment file or reuse local example credentials in a public deployment.

##### Responsibilities and invariants

The artifact contains placeholders and private local defaults only. Optional recipe variables are documented together so profile upgrades do not require discovering hidden settings.

##### Complete canonical artifact

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

##### Alternatives and trade-offs

`python-decouple` (see [settings](#srccoresettingsreadmemd)) reads and casts every variable in one call, so this reference has no hand-rolled parsing helpers to keep in sync.

##### Required tests

Secret-scan the repository and test every production-required variable.

##### Related standards

See [settings](#srccoresettingsreadmemd) and [security](#docssecuritymd).

### gitignore.md

#### Generated Project Ignore Rules

##### Purpose and when to use it

This artifact keeps reconstructed local state out of version control.

##### Complete canonical artifact

<!-- artifact: .gitignore; profiles: base -->
```gitignore
.env
.env.*
!.env.example
.venv/
__pycache__/
*.py[cod]
*.sqlite3
.coverage
coverage.xml
htmlcov/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.ty/
.data/
media/
staticfiles/
dist/
build/
*.egg-info/
.DS_Store
.idea/
.vscode/
```

##### Responsibilities and invariants

The example environment file remains trackable. Migrations and `uv.lock` must never be ignored.

##### Required tests

Inspect `git status` after local setup and test execution.

### gunicorn.conf.md

#### Gunicorn Configuration

##### Purpose and when to use it

Use Gunicorn for synchronous REST under WSGI.

##### Complete canonical artifact

<!-- artifact: gunicorn.conf.py; profiles: base -->
```python
import multiprocessing

from decouple import config

bind = config("GUNICORN_BIND", default="0.0.0.0:8000")
workers = config("GUNICORN_WORKERS", default=min(multiprocessing.cpu_count() * 2 + 1, 8), cast=int)
worker_class = "sync"
timeout = config("GUNICORN_TIMEOUT", default=30, cast=int)
graceful_timeout = config("GUNICORN_GRACEFUL_TIMEOUT", default=30, cast=int)
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
capture_output = True
```

##### Responsibilities and invariants

Bound worker counts prevent accidental overcommit. Long-lived realtime connections are not served by sync workers.

##### Required tests

Smoke-test startup, graceful termination, liveness, and one authenticated endpoint.

### makefile.md

#### Project Commands

##### Purpose and when to use it

The reconstructed Makefile provides memorable local commands while keeping the underlying commands visible.

##### Complete canonical artifact

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

##### Responsibilities and invariants

Commands do not rewrite migrations, erase databases, buckets, or volumes, and do not hide environment selection.

##### Required tests

Run every read-only validation target in CI.

### pre-commit-config.md

#### pre-commit Configuration

##### Purpose and when to use it

Use pre-commit as a fast local gate; CI remains authoritative.

##### Complete canonical artifact

<!-- artifact: .pre-commit-config.yaml; profiles: base -->
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.0
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

##### Alternatives and trade-offs

Auto-fixes are useful locally; CI runs read-only checks.

##### Required tests

Run `pre-commit run --all-files` in a reconstructed project.

### pyproject.md

#### Python Project Configuration

##### Purpose and when to use it

One `base` artifact pins the minimal REST stack and development tools.
Every other module contributes a small dependency-fragment (see
[dependency fragments](#docsreconstructionmd)) that
`reconstruct` merges into this file's `dependencies`, `dev`, and
`tool.pytest.ini_options` placeholders for whatever module set was
requested — there is no longer a separate fully-duplicated `pyproject.toml`
per legacy profile. Exact pins make the 2026-07-26 snapshot reviewable;
`uv.lock`, generated once per reconstruction (see
[dependency lock generation](#docsreconstructionmd)),
remains the installation authority.

##### When not to use it

Do not copy the full dependency set into a service that does not use those
capabilities — request only the modules it needs.

##### Responsibilities and invariants

Python, Django, DRF, Ruff, and `ty` agree on Python 3.14. Django migrations
are linted for syntax but excluded from style churn. Coverage includes
branches. Every dependency-fragment target must have a matching placeholder
in this artifact, or reconstruction fails fast (see
[reconstruction](#docsreconstructionmd)).

##### Complete canonical artifacts

<!-- artifact: pyproject.toml; profiles: base -->
```toml
[project]
name = "django-standard-api"
version = "0.1.0"
description = "Generic account-scoped Django REST API"
readme = "README.md"
requires-python = ">=3.14,<3.15"
dependencies = [
  "Django==6.0.7",
  "django-cors-headers==4.9.0",
  "django-filter==26.1",
  "djangorestframework==3.17.1",
  "djangorestframework-simplejwt==5.5.1",
  "gunicorn==26.0.0",
  "psycopg[binary]==3.3.4",
  "python-decouple==3.8",
  # {{FRAGMENT:dependencies}}
]

[dependency-groups]
dev = [
  "coverage==7.15.2",
  "freezegun==1.5.5",
  "pre-commit==4.6.1",
  "pytest==9.1.1",
  "pytest-django==4.12.0",
  "ruff==0.16.0",
  "ty==0.0.63",
  # {{FRAGMENT:dev}}
]

[tool.uv]
package = false
default-groups = ["dev"]

[tool.ruff]
target-version = "py314"
line-length = 100
src = ["src"]
extend-exclude = [".venv", ".data", "staticfiles", "media"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "DJ", "RUF"]
ignore = ["DJ001"]

[tool.ruff.lint.isort]
known-first-party = ["apps", "core"]

[tool.ruff.lint.per-file-ignores]
"**/migrations/*.py" = ["E501", "RUF012"]
"**/tests/*.py" = ["B011"]
"src/core/settings/__init__.py" = ["F401", "F403"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings"
pythonpath = ["src"]
python_files = ["test_*.py"]
addopts = "-ra --strict-config --strict-markers"
markers = [
  "integration: requires external infrastructure",
  "realtime: exercises ASGI or WebSocket behavior",
]
# {{FRAGMENT:pytest}}

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["*/migrations/*", "*/tests/*", "src/core/*", "src/manage.py"]

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 90
exclude_also = [
  "if TYPE_CHECKING:",
  "if __name__ == .__main__.:",
]
```

##### Alternatives and trade-offs

Range constraints reduce update churn but make a handbook snapshot less
reproducible. Upgrade pins deliberately.

Splitting the six duplicated whole-file variants into one base file plus
per-module dependency-fragments removes the drift risk of editing a shared
line (like the `sentry-sdk` pin used to be) in six places; the cost is that
`pyproject.toml` can no longer be read as one flat, complete list without
running `reconstruct` — the fragments must be read alongside their owning
module doc to see the whole picture ahead of generation.

`ty` still has incomplete knowledge of Django's dynamic fields, managers,
and DRF generics. Use narrow suppressions at the dynamic boundary and retain
runtime tests; do not add blanket ignores.

##### Required tests

Run frozen sync, Ruff, `ty`, pytest/coverage, Django checks, and the
migration drift check for `base` and `full`. Confirm the merged
`pyproject.toml` for at least one non-alias module combination contains
exactly its resolved modules' dependency-fragments (see
[reconstruction](#docsreconstructionmd)).

##### Related standards

See [version snapshot](#docsversion-snapshotmd), [testing](#docstestingmd),
and [reconstruction](#docsreconstructionmd).

### pytest.md

#### pytest Configuration

##### Purpose and when to use it

Use pytest-django for deterministic unit and integration tests.

##### Complete canonical artifact

<!-- artifact: pytest.ini; profiles: base -->
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
pythonpath = src
python_files = test_*.py
addopts = -ra --strict-config --strict-markers
markers =
    integration: requires external infrastructure
    realtime: exercises ASGI or WebSocket behavior
```

##### Responsibilities and invariants

Unknown configuration and markers fail collection. External-service tests opt into explicit markers.

##### Required tests

Run the complete suite and collect tests in isolation.

### python-version.md

#### Python Version

##### Purpose and when to use it

The handbook snapshot targets Python 3.14.6.

##### Complete canonical artifact

<!-- artifact: .python-version; profiles: base -->
```text
3.14.6
```

##### Responsibilities and invariants

CI, containers, local `uv`, Ruff, and `ty` target the same Python line.

##### Required tests

Run `python --version` in each derived environment.

### uv-lock.md

#### Reproducible Dependency Locks

##### Purpose and when to use it

`uv.lock` is generated **after** reconstruction, not carried as a canonical
artifact in this handbook. With modules freely composable (see
[reconstruction](#docsreconstructionmd)), the number of possible module
combinations is combinatorially large; pre-baking a lock for each one, the
way this file once pre-baked six — one per legacy flat profile — does not
scale to fine-grained modules. This follows the same precedent already
established for migrations: [migration
generation](#docsreconstructionmd) regenerates
derivable migrations post-reconstruction instead of carrying them as
artifacts, and [dependency lock
generation](#docsreconstructionmd) does the same
for `uv.lock`.

##### When not to use it

Do not hand-edit a lock or reuse one after changing the resolved module set
— run `uv lock` again.

##### Responsibilities and invariants

After materializing a project (and running `makemigrations` for any plain
recipe app included), run:

```bash
uv lock
```

once, from the materialized project root. Commit the resulting `uv.lock`
in the derived project alongside the generated migrations. The lock
includes hashes and transitive metadata for exactly the dependencies the
resolved module set's `pyproject.toml` declares (see [project
configuration](#pyprojectmd)). The 2026-07-26 dependency snapshot targets
Python 3.14.6; lock resolution was also checked on the available Python
3.14 line.

##### Alternatives and trade-offs

Pre-baked, per-profile locks (this file's approach before modules became
composable) let every combination ship a reviewable, hash-pinned lock
without running `uv lock` at all — but only because there were exactly six
combinations to pre-bake. A composable module graph trades that
zero-step convenience for scalability: one `uv lock` invocation handles any
of the arbitrarily many resolvable module sets.

##### Required tests

Materialize at least `base` and one non-alias module combination, run
`uv lock` in each, and confirm `uv sync --frozen` succeeds against the
result.

##### Related standards

See [project configuration](#pyprojectmd), [reconstruction](#docsreconstructionmd),
and [version snapshot](#docsversion-snapshotmd).

### src/README.md

#### Base Project Reference Tree

This tree mirrors the reconstructed `src/` layout. Each implementation page explains one complete canonical artifact.

- [manage.py](#srcmanagemd)
- [core process configuration](#srccorereadmemd)
- [application packages](#srcappsreadmemd)

The base profile reconstructs authentication, one-account-per-user tenancy, Customer CRUD, request IDs, error envelopes, JWT lifecycle, health checks, admin, migrations, and tests.

### src/apps/README.md

#### Application reference tree

This directory mirrors the application layer of the base project. Each child
package owns one cohesive concern and may depend only on packages below it in
the following direction:

`common` → `authentication` → `account` → `api` and `customer`.

The empty package artifact makes `apps` importable without adding runtime
behavior.

<!-- artifact: src/apps/__init__.py; profiles: base,full -->
```python
"""Project application packages."""
```

##### Related standards

- [Common foundations](#srcappscommonreadmemd)
- [API boundary](#srcappsapireadmemd)
- [Customer example](#srcappscustomerreadmemd)

### src/apps/account/README.md

#### Account tenancy

##### Purpose and when to use it

Use this package for the base project's deliberately simple tenancy model:
every user owns exactly one account and every tenant record references it.

##### When not to use it

Do not use this model when users can join multiple accounts. Adopt the
multi-account recipe and make account selection explicit instead.

##### Responsibilities and invariants

- `Account.user` is one-to-one and cannot be null.
- Inactive accounts cannot access account-owned endpoints.
- Every account-owned lookup scopes by account before object lookup.

##### Complete canonical artifact

<!-- artifact: src/apps/account/__init__.py; profiles: base,full -->
```python
"""Single-account tenancy primitives."""
```

##### Alternatives and trade-offs

One account per user removes ambiguous request context. It does not model teams,
invitations, or role-bearing memberships.

##### Required tests

Registration must create one account; tenant tests must prove cross-account
reads, updates, and deletes return not-found.

##### Related standards

- [Account models](#srcappsaccountmodelsmd)
- [Customer isolation](#srcappscustomerreadmemd)

### src/apps/account/admin.md

#### Account administration

##### Purpose and when to use it

Provide staff with a searchable account status view.

##### When not to use it

The admin is not a customer-facing tenancy API.

##### Responsibilities and invariants

Account ownership is read-only after creation to avoid accidental tenant
transfer.

##### Complete canonical artifact

<!-- artifact: src/apps/account/admin.py; profiles: base,full -->
```python
from django.contrib import admin

from apps.account.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__email",)
    readonly_fields = ("user", "created_at", "updated_at")
```

##### Alternatives and trade-offs

A dedicated operations UI can enforce richer workflows but adds a separate
surface to secure and maintain.

##### Required tests

Admin smoke tests verify the changelist for an authorized staff user.

##### Related standards

- [Account models](#srcappsaccountmodelsmd)

### src/apps/account/apps.md

#### Account application configuration

##### Purpose and when to use it

Register the account models without startup side effects.

##### When not to use it

Do not create accounts from signals in `ready()`; registration owns that
transaction explicitly.

##### Responsibilities and invariants

The application label is a migration contract.

##### Complete canonical artifact

<!-- artifact: src/apps/account/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.account"
```

##### Alternatives and trade-offs

Signals appear convenient but obscure transaction boundaries and complicate
bulk imports.

##### Required tests

`manage.py check` and migration checks validate registration.

##### Related standards

- [Registration service](#srcappsauthenticationservicesmd)

### src/apps/account/models.md

#### Account and account-owned models

##### Purpose and when to use it

Use `Account` as request tenancy context and inherit `AccountOwnedModel` for
every record whose visibility belongs to one account.

##### When not to use it

Global reference data and user-owned security records should not inherit the
tenant base.

##### Responsibilities and invariants

- Deleting a user deletes its single account and account-owned data.
- The abstract foreign key uses a predictable `account` field.
- Models do not infer an account from process-local or global state.

##### Complete canonical artifact

<!-- artifact: src/apps/account/models.py; profiles: base,full -->
```python
from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Account(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account",
    )
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Account({self.pk})"


class AccountOwnedModel(TimeStampedModel):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )

    class Meta:
        abstract = True
```

##### Alternatives and trade-offs

A membership table supports collaboration but requires an explicit active
account strategy. The base keeps the safer one-to-one invariant.

##### Required tests

Test the one-to-one constraint, cascade behavior, and inactive-account denial.

##### Related standards

- [Account creation](#srcappsaccountservicesmd)
- [Request scoping](#srcappsapiviewsmd)

### src/apps/account/services.md

#### Account creation service

##### Purpose and when to use it

Call this service inside registration or an administrative provisioning
transaction.

##### When not to use it

Do not call it on every login or hide it in a model signal.

##### Responsibilities and invariants

The operation is idempotent for one user and never changes an existing
account's active state.

##### Complete canonical artifact

<!-- artifact: src/apps/account/services.py; profiles: base,full -->
```python
from apps.account.models import Account
from apps.authentication.models import User


def ensure_account(*, user: User) -> tuple[Account, bool]:
    return Account.objects.get_or_create(user=user)
```

##### Alternatives and trade-offs

`get_or_create` makes provisioning retry-safe. A plain create is stricter but
turns harmless delivery retries into integrity failures.

##### Required tests

Calling the service twice returns the same account and reports creation once.

##### Related standards

- [Registration transaction](#srcappsauthenticationservicesmd)

### src/apps/api/README.md

#### API boundary

##### Purpose and when to use it

Use this package for cross-cutting HTTP policy: versioned routing, request IDs,
error envelopes, health probes, authentication defaults, pagination, and
account-scoped view bases.

##### When not to use it

Do not place domain models or business workflows in the API package.

##### Responsibilities and invariants

- Authenticated endpoints deny requests without an active account.
- Errors have one stable envelope and include the request ID.
- Liveness performs no dependency I/O; readiness verifies the database.
- Pagination ordering is unique and stable.
- Default API throttling applies sustained and burst limits; sensitive routes
  add named scopes.

##### Complete canonical artifact

<!-- artifact: src/apps/api/__init__.py; profiles: base,full -->
```python
"""Versioned API infrastructure."""
```

##### Reusable burst throttle

Use a second user throttle with its own scope to constrain short bursts
independently from the sustained authenticated-user limit. For anonymous
requests, DRF's `UserRateThrottle` falls back to the client identifier, so the
burst policy also applies before authentication.

<!-- artifact: src/apps/api/throttling.py; profiles: base,full -->
```python
from rest_framework.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"
```

##### Alternatives and trade-offs

Per-application HTTP helpers reduce central coupling but can fragment public
behavior. Only genuinely cross-cutting policy belongs here. Additional
`SimpleRateThrottle` subclasses are appropriate when a limit needs a different
identity key, but keys derived from email addresses or other submitted
identifiers must be normalized, non-enumerable, and privacy-reviewed.

##### Required tests

Test health states, request ID propagation, envelope normalization,
authentication defaults, burst and scoped throttling, and inactive-account
denial.

##### Related standards

- [API views](#srcappsapiviewsmd)
- [Exception handling](#srcappsapiexceptionsmd)
- [Request IDs](#srcappsapimiddlewaremd)
- [API design](#docsapi-designmd)

### src/apps/api/apps.md

#### API application configuration

##### Purpose and when to use it

Register API infrastructure with a stable Django application label.

##### When not to use it

Do not start network clients or run health checks at import time.

##### Responsibilities and invariants

Application startup remains deterministic and side-effect free.

##### Complete canonical artifact

<!-- artifact: src/apps/api/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
```

##### Alternatives and trade-offs

Implicit configuration is shorter but hides the application contract.

##### Required tests

`manage.py check` verifies application loading.

##### Related standards

- [API boundary](#srcappsapireadmemd)

### src/apps/api/exceptions.md

#### Consistent API exception handling

##### Purpose and when to use it

Configure this handler as DRF's global `EXCEPTION_HANDLER` to normalize all API
errors.

##### When not to use it

Do not return raw exception strings, tracebacks, SQL, or configuration values.

##### Responsibilities and invariants

Every error contains a stable code, human-readable message, structured details,
and the request ID. Unexpected errors are logged and returned as a generic 500.

##### Complete canonical artifact

<!-- artifact: src/apps/api/exceptions.py; profiles: base,full -->
```python
import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.api.middleware import get_request_id

logger = logging.getLogger(__name__)


def _error_code(data: Any) -> str:
    if hasattr(data, "code"):
        return str(data.code)
    if isinstance(data, dict) and hasattr(data.get("detail"), "code"):
        return str(data["detail"].code)
    return "validation_error" if isinstance(data, (dict, list)) else "api_error"


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    request = context.get("request")
    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                    "details": None,
                    "request_id": get_request_id(request),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    details = response.data
    message = "The request could not be completed."
    if not isinstance(details, (dict, list)):
        message = str(details)
    elif isinstance(details, dict) and "detail" in details:
        message = str(details["detail"])
    response.data = {
        "error": {
            "code": _error_code(details),
            "message": message,
            "details": details,
            "request_id": get_request_id(request),
        }
    }
    return response
```

##### Alternatives and trade-offs

RFC 9457 problem details is a good interoperable alternative. This smaller
envelope keeps the example explicit and stable for clients.

##### Required tests

Cover validation, authentication, not-found, domain, and unexpected exceptions;
assert internal messages never leak.

##### Related standards

- [Request IDs](#srcappsapimiddlewaremd)
- [Domain exceptions](#srcappscommonexceptionsmd)

### src/apps/api/health.md

#### Health checks

##### Purpose and when to use it

Use liveness to detect a running process and readiness to decide whether the
instance can serve traffic.

##### When not to use it

Do not call third-party services from liveness or expose exception details.

##### Responsibilities and invariants

The database readiness check is bounded by the database connection timeout and
returns only a boolean status.

##### Complete canonical artifact

<!-- artifact: src/apps/api/health.py; profiles: base,full -->
```python
from django.db import DatabaseError, connection


def database_is_ready() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except DatabaseError:
        return False
```

##### Alternatives and trade-offs

Deep dependency checks offer more detail but can amplify an outage and cause
healthy processes to restart. Keep optional dependencies out of base readiness.

##### Required tests

Mock success and database failure without requiring an external database outage.

##### Related standards

- [Health views](#srcappsapiviewsmd)

### src/apps/api/middleware.md

#### Request ID middleware

##### Purpose and when to use it

Assign one correlation identifier to every HTTP request and return it in the
`X-Request-ID` response header.

##### When not to use it

Do not treat a caller-supplied request ID as authentication or authorization.

##### Responsibilities and invariants

Only short identifiers containing conservative visible characters are trusted;
all other values are replaced with a random UUID.

##### Complete canonical artifact

<!-- artifact: src/apps/api/middleware.py; profiles: base,full -->
```python
import logging
import re
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
current_request_id: ContextVar[str] = ContextVar("request_id", default="unknown")


class RequestIDMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        supplied = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = supplied if REQUEST_ID_PATTERN.fullmatch(supplied) else str(uuid.uuid4())
        request.request_id = request_id  # ty: ignore[unresolved-attribute]
        token = current_request_id.set(request_id)
        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            current_request_id.reset(token)


def get_request_id(request: Any) -> str:
    return str(getattr(request, "request_id", "unknown"))


class RequestIDLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id.get()
        return True
```

##### Alternatives and trade-offs

Always generating a server ID avoids untrusted input but breaks correlation
across a trusted gateway. Validation preserves that chain without accepting
arbitrary header content.

##### Required tests

Test generated, accepted, rejected, and response-propagated identifiers.

##### Related standards

- [Error envelopes](#srcappsapiexceptionsmd)

### src/apps/api/pagination.md

#### Stable cursor pagination

##### Purpose and when to use it

Use cursor pagination for mutable collections where offset pages would skip or
duplicate records.

##### When not to use it

Use explicit bounded pages when clients require random page access or a total
count.

##### Responsibilities and invariants

Ordering ends with the unique primary key, page size is bounded, and clients
treat cursors as opaque.

##### Complete canonical artifact

<!-- artifact: src/apps/api/pagination.py; profiles: base,full -->
```python
from rest_framework.pagination import CursorPagination


class StableCursorPagination(CursorPagination):
    page_size = 50
    cursor_query_param = "cursor"
    ordering = ("-created_at", "-id")
```

##### Alternatives and trade-offs

Cursor pagination is stable and efficient but cannot provide arbitrary page
jumps or a cheap exact total.

##### Required tests

Insert tied timestamps and records between requests; assert no duplicates or
omissions while following cursors.

##### Related standards

- [Customer collection](#srcappscustomerviewsmd)

### src/apps/api/tests/README.md

#### API infrastructure tests

These tests cover routing, health states, request IDs, and error normalization.

<!-- artifact: src/apps/api/tests/__init__.py; profiles: base,full -->
```python
"""API infrastructure tests."""
```

##### Related standards

- [API boundary](#srcappsapireadmemd)

### src/apps/api/tests/views/README.md

#### API view tests

Keep endpoint tests grouped by the HTTP boundary they exercise.

<!-- artifact: src/apps/api/tests/views/__init__.py; profiles: base,full -->
```python
"""API endpoint tests."""
```

### src/apps/api/tests/views/test_health.md

#### Health endpoint tests

##### Purpose and when to use it

Verify public liveness and database-aware readiness behavior.

##### When not to use it

These unit tests do not replace a deployed probe smoke test.

##### Responsibilities and invariants

Liveness is always dependency-free; readiness returns 503 when the database
check fails.

##### Complete canonical artifact

<!-- artifact: src/apps/api/tests/views/test_health.py; profiles: base,full -->
```python
from unittest.mock import MagicMock, patch

from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def test_liveness_is_public(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:live")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    assert response["X-Request-ID"]


@patch("apps.api.health.connection.cursor")
def test_readiness_returns_ok_when_database_is_ready(
    cursor_factory: MagicMock,
    api_client: APIClient,
) -> None:
    # Arrange
    url = reverse("api:ready")
    cursor = cursor_factory.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1,)

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    cursor.execute.assert_called_once_with("SELECT 1")


@patch("apps.api.health.connection.cursor", side_effect=DatabaseError)
def test_readiness_returns_503_when_database_is_unavailable(
    cursor_factory: MagicMock,
    api_client: APIClient,
) -> None:
    # Arrange
    url = reverse("api:ready")

    # Act
    response = api_client.get(
        url,
        HTTP_X_REQUEST_ID="gateway-request-42",
    )

    # Assert
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"status": "unavailable"}
    assert response["X-Request-ID"] == "gateway-request-42"
    cursor_factory.assert_called_once_with()
```

##### Alternatives and trade-offs

Integration tests against PostgreSQL catch driver and credential failures; unit
tests make success and outage branches deterministic.

##### Required tests

Run both unit tests and a deployed readiness probe.

##### Related standards

- [Health implementation](#srcappsapihealthmd)
- [Request ID middleware](#srcappsapimiddlewaremd)

### src/apps/api/urls.md

#### Versioned API routes

##### Purpose and when to use it

Compose the base API under the project-level `/api/v1/` prefix.

##### When not to use it

Do not mount admin, metrics, or static media below the public API namespace.

##### Responsibilities and invariants

Every application owns its child URL configuration and namespace.

##### Complete canonical artifact

<!-- artifact: src/apps/api/urls.py; profiles: base,full -->
```python
from django.urls import include, path

from apps.api.views import LivenessView, ReadinessView

app_name = "api"

urlpatterns = [
    path("live/", LivenessView.as_view(), name="live"),
    path("ready/", ReadinessView.as_view(), name="ready"),
    path("auth/", include("apps.authentication.urls", namespace="auth")),
    path("customers/", include("apps.customer.urls", namespace="customers")),
]
```

##### Alternatives and trade-offs

Header-based versioning keeps URLs stable but is harder to inspect, cache, and
link. Path versioning makes compatibility boundaries explicit.

##### Required tests

Reverse all public route names and assert the expected versioned paths.

##### Related standards

- [Authentication routes](#srcappsauthenticationurlsmd)
- [Customer routes](#srcappscustomerurlsmd)

### src/apps/api/views.md

#### API view foundations and probes

##### Purpose and when to use it

Use these views for health probes and inherit `AccountScopedViewSet` for
account-owned resources.

##### When not to use it

Global or public resources need explicit permission and query policy rather
than inheriting account scoping.

##### Responsibilities and invariants

The account is derived from the authenticated user, checked for activity, and
applied before any object lookup.

##### Complete canonical artifact

<!-- artifact: src/apps/api/views.py; profiles: base,full -->
```python
from typing import Any

from django.http import Http404
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.models import Account
from apps.api.health import database_is_ready
from apps.common.exceptions import AccountUnavailable


def account_for_request(request: Request) -> Account:
    account = Account.objects.filter(user=request.user).first()
    if account is None:
        raise Http404
    if not account.is_active:
        raise AccountUnavailable
    return account


class AccountScopedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_account(self) -> Account:
        return account_for_request(self.request)

    def get_queryset(self) -> Any:
        return super().get_queryset().filter(account=self.get_account())


class LivenessView(APIView):
    authentication_classes: tuple[()] = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes: tuple[()] = ()

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


class ReadinessView(APIView):
    authentication_classes: tuple[()] = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes: tuple[()] = ()

    def get(self, request: Request) -> Response:
        ready = database_is_ready()
        return Response(
            {"status": "ok" if ready else "unavailable"},
            status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
```

##### Alternatives and trade-offs

Injecting account context in middleware can serve non-DRF views too, but it
makes public-route exceptions and authentication order less visible. Health
probes explicitly bypass application throttles so traffic spikes cannot turn a
healthy deployment into a failed orchestrator probe.

##### Required tests

Prove account filtering occurs for list and detail actions and inactive accounts
are rejected. Test both health statuses.

##### Related standards

- [Account model](#srcappsaccountmodelsmd)
- [Customer ViewSet](#srcappscustomerviewsmd)

### src/apps/authentication/README.md

#### Authentication and user identity

##### Purpose and when to use it

Use this package for email-based identity, registration, current-user data, and
the JWT lifecycle.

##### When not to use it

Do not add social login, organization roles, or vendor-specific identity flows
to the base project.

##### Responsibilities and invariants

- Email is normalized, unique, and is the login identifier.
- Passwords pass Django's configured validators and are never returned.
- Registration creates the user and its account in one transaction.
- Refresh tokens rotate and old tokens are blacklisted by settings; logout
  explicitly blacklists the submitted refresh token.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/__init__.py; profiles: base,full -->
```python
"""Email identity and JWT endpoints."""
```

##### Alternatives and trade-offs

Cookie-bound sessions are a strong choice for same-origin browser applications.
Bearer JWTs fit independently deployed API clients but require careful storage,
rotation, revocation, and short access-token lifetimes.

##### Required tests

Cover normalization, duplicate registration, password validation, login,
rotation, revocation, logout, and unauthenticated access.

##### Related standards

- [User model](#srcappsauthenticationmodelsmd)
- [JWT endpoints](#srcappsauthenticationurlsmd)
- [Account provisioning](#srcappsauthenticationservicesmd)

### src/apps/authentication/admin.md

#### Custom user administration

##### Purpose and when to use it

Give authorized staff a safe interface for email-based users.

##### When not to use it

Do not expose the Django admin to end users or use it as a public account API.

##### Responsibilities and invariants

Password changes use Django's hashed-password form and email remains the login
identifier.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/admin.py; profiles: base,full -->
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import (
    UserChangeForm as DjangoUserChangeForm,
)
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
)

from apps.authentication.models import User


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email",)


class UserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal information", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff"),
            },
        ),
    )
```

##### Alternatives and trade-offs

A separate staff portal supports tighter workflows but duplicates mature admin
security and form behavior.

##### Required tests

Smoke-test user creation and change views with an authorized staff client.

##### Related standards

- [User model](#srcappsauthenticationmodelsmd)

### src/apps/authentication/apps.md

#### Authentication application configuration

##### Purpose and when to use it

Register the custom user application before the first migration.

##### When not to use it

Never change `AUTH_USER_MODEL` after production migrations exist.

##### Responsibilities and invariants

The app label and user model name form a permanent schema contract.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
```

##### Alternatives and trade-offs

Django's default user is sufficient when username login is acceptable. A custom
model is easiest to adopt at project creation.

##### Required tests

`manage.py check` must resolve `authentication.User` as the configured model.

##### Related standards

- [User model](#srcappsauthenticationmodelsmd)

### src/apps/authentication/models.md

#### Email-based custom user

##### Purpose and when to use it

Use this model when email is the sole login identifier from the start of a
project.

##### When not to use it

Do not swap user models after a deployed database already references Django's
default user.

##### Responsibilities and invariants

- `username` is removed rather than mirrored from email.
- Manager methods normalize email and hash passwords.
- Superuser creation rejects contradictory privilege flags.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/models.py; profiles: base,full -->
```python
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

if TYPE_CHECKING:
    from apps.account.models import Account


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ) -> User:
        if not email:
            raise ValueError("An email address is required.")
        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields["is_staff"] is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("A superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    if TYPE_CHECKING:
        account: Account

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []  # ty: ignore[invalid-attribute-override]

    objects = UserManager()

    def __str__(self) -> str:
        return str(self.email)
```

##### Alternatives and trade-offs

Subclassing `AbstractUser` retains Django permissions and admin behavior. A
smaller `AbstractBaseUser` model offers more control but requires more security
plumbing.

##### Required tests

Test email normalization, password hashing, duplicate rejection, and superuser
flag validation.

##### Related standards

- [Migration generation](#docsreconstructionmd)
- [User administration](#srcappsauthenticationadminmd)

### src/apps/authentication/serializers.md

#### Authentication serializers

##### Purpose and when to use it

Validate registration, current-user output, and refresh-token logout payloads.

##### When not to use it

Token signature and claim validation belong to Simple JWT, not custom fields.

##### Responsibilities and invariants

Passwords are write-only, Django password validators run with user context, and
email uniqueness errors are deterministic.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/serializers.py; profiles: base,full -->
```python
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.authentication.models import User
from apps.authentication.services import register_user


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
        read_only_fields = fields


class RegistrationSerializer(serializers.Serializer[User]):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=150, allow_blank=True, default="")

    def validate_email(self, value: str) -> str:
        normalized = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        candidate = User(
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        validate_password(attrs["password"], user=candidate)
        return attrs

    def create(self, validated_data: dict[str, str]) -> User:
        return register_user(**validated_data)


class LogoutSerializer(serializers.Serializer[dict[str, str]]):
    refresh = serializers.CharField(trim_whitespace=False)
```

##### Alternatives and trade-offs

Confirm-password fields can catch client typing errors, but API clients can
perform that comparison locally without transmitting duplicate secrets.

##### Required tests

Test normalization, duplicate email, weak password rejection, and that response
serialization excludes password fields.

##### Related standards

- [Registration service](#srcappsauthenticationservicesmd)
- [Authentication views](#srcappsauthenticationviewsmd)

### src/apps/authentication/services.md

#### Atomic registration service

##### Purpose and when to use it

Use this service for the multi-model registration workflow.

##### When not to use it

Simple user field updates belong in serializers or model forms; they do not
need a service layer.

##### Responsibilities and invariants

User and account creation commit together, and duplicate email races surface as
a normal validation error at the API boundary.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/services.py; profiles: base,full -->
```python
from django.db import transaction

from apps.account.services import ensure_account
from apps.authentication.models import User


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    ensure_account(user=user)
    return user
```

##### Alternatives and trade-offs

A post-save signal reduces call-site code but hides failures and can create
partial side effects outside the intended transaction.

##### Required tests

Force account creation to fail and assert the user is rolled back; retry
account provisioning independently to prove idempotency.

##### Related standards

- [Account service](#srcappsaccountservicesmd)
- [Registration endpoint](#srcappsauthenticationviewsmd)

### src/apps/authentication/tests/README.md

#### Authentication tests

The package covers registration, user output, and the full JWT refresh and
revocation lifecycle.

<!-- artifact: src/apps/authentication/tests/__init__.py; profiles: base,full -->
```python
"""Authentication application tests."""
```

##### Related standards

- [Authentication boundary](#srcappsauthenticationreadmemd)

### src/apps/authentication/tests/helpers.md

#### Authentication test helpers

##### Purpose and when to use it

Keep token acquisition explicit without duplicating endpoint payloads.

##### When not to use it

Tests for login failure should make their own request and assert the response.

##### Responsibilities and invariants

The helper asserts successful login before returning both token strings.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/helpers.py; profiles: base,full -->
```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

DEFAULT_PASSWORD = "Correct-Horse-Battery-Staple-42"


def obtain_tokens(
    *,
    client: APIClient,
    email: str,
    password: str = DEFAULT_PASSWORD,
) -> tuple[str, str]:
    response = client.post(
        reverse("api:auth:token"),
        {"email": email, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    return payload["access"], payload["refresh"]
```

##### Alternatives and trade-offs

Constructing tokens directly is faster but bypasses the actual login contract.

##### Required tests

JWT lifecycle tests exercise this helper through the real endpoint.

##### Related standards

- [JWT lifecycle tests](#srcappsauthenticationteststest_tokensmd)

### src/apps/authentication/tests/test_me.md

#### Current-user endpoint tests

##### Purpose and when to use it

Verify authenticated user data is allow-listed and anonymous requests fail.

##### When not to use it

Do not infer JWT refresh behavior from this endpoint.

##### Responsibilities and invariants

Password, permission, and account internals are absent from the response.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_me.py; profiles: base,full -->
```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import User


@pytest.mark.django_db
def test_me_returns_allow_listed_user(
    authenticated_client: APIClient,
    user: User,
) -> None:
    # Arrange
    url = reverse("api:auth:me")

    # Act
    response = authenticated_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user.pk,
        "email": user.email,
        "first_name": "",
        "last_name": "",
    }


@pytest.mark.django_db
def test_me_requires_authentication(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:auth:me")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["request_id"]
```

##### Alternatives and trade-offs

Embedding account data can save a request but couples identity and tenancy
contracts. The base keeps the response narrow.

##### Required tests

Run both authenticated and anonymous cases for authentication changes.

##### Related standards

- [Authentication views](#srcappsauthenticationviewsmd)

### src/apps/authentication/tests/test_register.md

#### Registration tests

##### Purpose and when to use it

Verify the public registration transaction and validation contract.

##### When not to use it

Manager unit tests remain responsible for low-level user creation rules.

##### Responsibilities and invariants

A successful response excludes the password and creates exactly one account;
invalid input creates neither model.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_register.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User


@pytest.mark.django_db
def test_registration_creates_user_and_account(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:auth:register")
    payload = {
        "email": "New.User@EXAMPLE.com",
        "password": "Correct-Horse-Battery-Staple-42",
        "first_name": "New",
        "last_name": "User",
    }

    # Act
    response = api_client.post(
        url,
        payload,
    )
    user = User.objects.get(email="New.User@example.com")

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.json()) == {"id", "email", "first_name", "last_name"}
    assert user.check_password("Correct-Horse-Battery-Staple-42")
    assert Account.objects.filter(user=user, is_active=True).count() == 1


@pytest.mark.django_db
def test_duplicate_email_uses_error_envelope(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user_factory(email="duplicate@example.com")
    url = reverse("api:auth:register")
    registration = {
        "email": "duplicate@example.com",
        "password": "Correct-Horse-Battery-Staple-42",
    }

    # Act
    response = api_client.post(
        url,
        registration,
    )
    payload = response.json()["error"]

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert payload["code"] == "validation_error"
    assert payload["details"]["email"] == ["A user with this email already exists."]
    assert payload["request_id"]
    assert User.objects.filter(email="duplicate@example.com").count() == 1
```

##### Alternatives and trade-offs

Service-only tests diagnose transaction behavior precisely; endpoint tests also
lock serializer and envelope behavior.

##### Required tests

Add weak-password and forced account-failure cases when changing registration.

##### Related standards

- [Registration serializer](#srcappsauthenticationserializersmd)
- [Registration service](#srcappsauthenticationservicesmd)

### src/apps/authentication/tests/test_tokens.md

#### JWT lifecycle tests

##### Purpose and when to use it

Prove access authentication, refresh rotation, old-token blacklisting, and
explicit logout revocation.

##### When not to use it

Do not mock Simple JWT in lifecycle tests; mocks would bypass the security
properties under test.

##### Responsibilities and invariants

Old refresh tokens stop working immediately after rotation or logout while
newly issued access tokens authenticate.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/tests/test_tokens.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.helpers import DEFAULT_PASSWORD, obtain_tokens


@pytest.mark.django_db
def test_refresh_rotates_and_blacklists_old_token(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="jwt@example.com", password=DEFAULT_PASSWORD)
    access, refresh = obtain_tokens(client=api_client, email=user.email)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Act
    authenticated = api_client.get(reverse("api:auth:me"))
    api_client.credentials()
    rotated = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )
    reused = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )

    # Assert
    assert authenticated.status_code == status.HTTP_200_OK
    assert rotated.status_code == status.HTTP_200_OK
    assert rotated.json()["refresh"] != refresh
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="logout@example.com", password=DEFAULT_PASSWORD)
    access, refresh = obtain_tokens(client=api_client, email=user.email)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Act
    response = api_client.post(
        reverse("api:auth:logout"),
        {"refresh": refresh},
    )
    api_client.credentials()
    reused = api_client.post(
        reverse("api:auth:token-refresh"),
        {"refresh": refresh},
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED
```

##### Alternatives and trade-offs

Shorter access-token lifetime narrows the remaining logout window but increases
refresh traffic.

##### Required tests

Keep rotation, reuse denial, logout, and invalid-token cases in the base suite.

##### Related standards

- [JWT routes](#srcappsauthenticationurlsmd)
- [Authentication policy](#srcappsauthenticationreadmemd)

### src/apps/authentication/urls.md

#### Authentication URL surface

##### Purpose and when to use it

Mount a stable, namespaced JWT and identity API under `/api/v1/auth/`.

##### When not to use it

Do not expose token endpoints under multiple aliases; duplicated routes
complicate client migration and rate limiting.

##### Responsibilities and invariants

Token obtain, refresh, verify, logout, registration, and current-user routes
have explicit names. Public token operations use distinct throttle scopes so
credential checks and refresh traffic can be tuned independently.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/urls.py; profiles: base,full -->
```python
from django.urls import path

from apps.authentication.views import (
    LogoutView,
    MeView,
    RegistrationView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
)

app_name = "auth"

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "token/",
        ThrottledTokenObtainPairView.as_view(),
        name="token",
    ),
    path(
        "token/refresh/",
        ThrottledTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "token/verify/",
        ThrottledTokenVerifyView.as_view(),
        name="token-verify",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
```

##### Alternatives and trade-offs

An external identity provider can add federation and managed risk controls but
introduces network dependency and provider lifecycle concerns. IP-based
application throttling reduces accidental and low-volume abuse; credential
stuffing still requires edge controls, monitoring, and risk-aware
authentication policy.

##### Required tests

Reverse every named route, exercise the complete token lifecycle, and verify
that each public credential route returns 429 at its configured threshold.

##### Related standards

- [Authentication views](#srcappsauthenticationviewsmd)

### src/apps/authentication/views.md

#### Authentication API views

##### Purpose and when to use it

Expose registration, the current authenticated user, and explicit refresh-token
revocation.

##### When not to use it

Do not build custom access-token parsing or refresh rotation in these views.

##### Responsibilities and invariants

Public registration has no authentication class, uses a stricter named
throttle scope, returns all user output through an allow-list serializer, and
fails malformed logout tokens safely.

##### Complete canonical artifact

<!-- artifact: src/apps/authentication/views.py; profiles: base,full -->
```python
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.authentication.serializers import (
    LogoutSerializer,
    RegistrationSerializer,
    UserSerializer,
)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_scope = "token"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_scope = "token_refresh"


class ThrottledTokenVerifyView(TokenVerifyView):
    throttle_scope = "token_verify"


class RegistrationView(generics.CreateAPIView):
    authentication_classes: tuple[()] = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    throttle_scope = "registration"

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(
                {"detail": "The refresh token is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
```

##### Alternatives and trade-offs

Server-side sessions make revocation immediate. Short access tokens plus rotated
and blacklisted refresh tokens preserve stateless API authentication while
bounding revocation delay. Small subclasses are preferable to passing undeclared
attributes to `as_view()`, which Django rejects.

##### Required tests

Cover public registration, authenticated `me`, invalid logout tokens, and
blacklisted refresh-token rejection.

##### Related standards

- [URL surface](#srcappsauthenticationurlsmd)
- [JWT tests](#srcappsauthenticationteststest_tokensmd)

### src/apps/common/README.md

#### Common application foundations

##### Purpose and when to use it

Use this package for small, dependency-free primitives shared by multiple
domain applications.

##### When not to use it

Do not place business workflows, tenant policy, or vendor integrations here.

##### Responsibilities and invariants

- Shared models remain abstract.
- Exceptions expose stable machine codes and safe public messages.
- The package imports no domain application.

##### Complete canonical artifact

<!-- artifact: src/apps/common/__init__.py; profiles: base,full -->
```python
"""Dependency-free application primitives."""
```

##### Alternatives and trade-offs

Keeping primitives in their first owning application reduces indirection. Move
code here only after at least two applications genuinely share it.

##### Required tests

Concrete models inheriting the timestamp base are exercised by their owning
application tests.

##### Related standards

- [Shared models](#srcappscommonmodelsmd)
- [Public exceptions](#srcappscommonexceptionsmd)

### src/apps/common/apps.md

#### Common Django application configuration

##### Purpose and when to use it

Register the common package with Django so model metadata is deterministic.

##### When not to use it

Do not perform startup I/O or import domain models from `ready()`.

##### Responsibilities and invariants

The application label and default primary-key type must remain stable after the
first migration ships.

##### Complete canonical artifact

<!-- artifact: src/apps/common/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
```

##### Alternatives and trade-offs

Implicit configuration is shorter but makes application metadata less obvious.

##### Required tests

`manage.py check` validates application loading.

##### Related standards

- [Common foundations](#srcappscommonreadmemd)

### src/apps/common/exceptions.md

#### Safe domain exceptions

##### Purpose and when to use it

Raise these exceptions when an authenticated request cannot operate in its
account context.

##### When not to use it

Do not expose database errors or internal exception messages through new
`APIException` subclasses.

##### Responsibilities and invariants

Each exception has a stable code, an appropriate HTTP status, and a public
message that contains no sensitive state.

##### Complete canonical artifact

<!-- artifact: src/apps/common/exceptions.py; profiles: base,full -->
```python
from rest_framework import status
from rest_framework.exceptions import APIException


class AccountUnavailable(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "The account is not available."
    default_code = "account_unavailable"
```

##### Alternatives and trade-offs

Returning not-found can conceal resource existence. This exception is used only
for the caller's own inactive account; cross-account object lookups still
return not-found.

##### Required tests

API tests assert both the status and the normalized error envelope.

##### Related standards

- [API exception handler](#srcappsapiexceptionsmd)

### src/apps/common/models.md

#### Timestamped models

##### Purpose and when to use it

Inherit `TimeStampedModel` for persistent domain records that need creation and
last-modification timestamps.

##### When not to use it

Do not inherit it for join tables or immutable event records whose timestamps
have different semantics.

##### Responsibilities and invariants

- Timestamps are server assigned and read-only at the API boundary.
- The base is abstract and creates no table.
- Concrete models choose indexes based on their query patterns.

##### Complete canonical artifact

<!-- artifact: src/apps/common/models.py; profiles: base,full -->
```python
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

##### Alternatives and trade-offs

Database-generated timestamps improve cross-writer consistency but require
database-specific expressions. Django-managed values are portable and adequate
when the application is the only writer.

##### Required tests

Domain model tests verify timestamps are populated and updates advance
`updated_at`.

##### Related standards

- [Account-owned models](#srcappsaccountmodelsmd)

### src/apps/conftest.md

#### Base pytest fixtures

##### Purpose and when to use it

Provide explicit API clients and account-bearing users shared by application
tests.

##### When not to use it

Do not hide the state relevant to a test behind large implicit fixture graphs.

##### Responsibilities and invariants

Every ordinary user fixture has exactly one active account and passwords are set
through the manager.

##### Complete canonical artifact

<!-- artifact: src/conftest.py; profiles: base,full -->
```python
from typing import Any

import pytest
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_factory(db: None) -> Any:
    def create_user(
        *,
        email: str = "user@example.com",
        password: str = "Correct-Horse-Battery-Staple-42",
        account_active: bool = True,
    ) -> User:
        user = User.objects.create_user(email=email, password=password)
        Account.objects.create(user=user, is_active=account_active)
        return user

    return create_user


@pytest.fixture
def user(user_factory: Any) -> User:
    return user_factory()


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client
```

##### Alternatives and trade-offs

Model Bakery or Factory Boy scales richer fixture graphs but adds a dependency
and another abstraction to this small base.

##### Required tests

The suite itself validates fixture setup on every database-backed test.

##### Related standards

- [Authentication test helpers](#srcappsauthenticationtestshelpersmd)

### src/apps/customer/README.md

#### Account-isolated Customer CRUD

##### Purpose and when to use it

Use this application as the base example of straightforward Django models,
`ModelSerializer`, and DRF `ModelViewSet` CRUD.

##### When not to use it

Do not introduce a service or selector merely to forward one ORM call. Use
services for transactions or effects and selectors for genuinely reusable,
complex reads.

##### Responsibilities and invariants

- Every Customer belongs to one account.
- Querysets are account-scoped before retrieve, update, and delete.
- The request cannot choose or change the account foreign key.
- Search and ordering use allow-lists; pagination has stable ordering.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/__init__.py; profiles: base,full -->
```python
"""Account-isolated customer records."""
```

##### Alternatives and trade-offs

Separate request and response serializers can provide stricter asymmetry, but a
small CRUD resource remains clearer with one carefully configured
`ModelSerializer`.

##### Required tests

Cover CRUD, authentication, filtering, stable pagination, inactive accounts,
and cross-account denial for reads, updates, and deletes.

##### Related standards

- [Customer model](#srcappscustomermodelsmd)
- [Customer API](#srcappscustomerviewsmd)
- [Account scoping](#srcappsapiviewsmd)

### src/apps/customer/admin.md

#### Customer administration

##### Purpose and when to use it

Allow authorized staff to inspect generic Customer records.

##### When not to use it

Do not rely on admin list filters as a substitute for application-level tenant
authorization.

##### Responsibilities and invariants

Ownership and timestamps are read-only; searches avoid notes to limit expensive
unbounded text scans.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/admin.py; profiles: base,full -->
```python
from django.contrib import admin

from apps.customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "account", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "phone", "account__user__email")
    readonly_fields = ("account", "created_at", "updated_at")
    ordering = ("-created_at", "-id")
```

##### Alternatives and trade-offs

Removing account records from admin entirely reduces support capability but
also reduces the impact of staff mistakes.

##### Required tests

Admin smoke tests verify list and change views for authorized staff.

##### Related standards

- [Customer model](#srcappscustomermodelsmd)

### src/apps/customer/apps.md

#### Customer application configuration

##### Purpose and when to use it

Register the Customer teaching application with Django.

##### When not to use it

Do not use startup hooks for customer data synchronization.

##### Responsibilities and invariants

The application label remains stable for schema and content-type references.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/apps.py; profiles: base,full -->
```python
from django.apps import AppConfig


class CustomerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customer"
```

##### Alternatives and trade-offs

Implicit app configuration is shorter but less explicit.

##### Required tests

`manage.py check` validates application loading.

##### Related standards

- [Customer application](#srcappscustomerreadmemd)

### src/apps/customer/models.md

#### Customer model

##### Purpose and when to use it

Store a generic contact record owned by one account.

##### When not to use it

Do not add authentication, billing, or vendor-specific fields to this teaching
model.

##### Responsibilities and invariants

Account ownership is mandatory, string output is safe for logs, and the default
index supports tenant-scoped newest-first listing.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/models.py; profiles: base,full -->
```python
from django.db import models

from apps.account.models import AccountOwnedModel


class Customer(AccountOwnedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    objects = models.Manager()

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = (
            models.Index(
                fields=("account", "-created_at", "-id"),
                name="customer_account_created_idx",
            ),
        )

    def __str__(self) -> str:
        return f"Customer({self.pk}, {self.name})"
```

##### Alternatives and trade-offs

Normalizing phone numbers and email addresses into separate models helps
multi-value contacts but adds joins and domain policy not needed for base CRUD.

##### Required tests

Test required ownership, default ordering, index migration parity, and timestamp
population.

##### Related standards

- [Account-owned base](#srcappsaccountmodelsmd)
- [Migration generation](#docsreconstructionmd)

### src/apps/customer/serializers.md

#### Customer serializer

##### Purpose and when to use it

Validate the small Customer CRUD contract directly from the model.

##### When not to use it

Use separate command and response serializers when write and read contracts
meaningfully diverge.

##### Responsibilities and invariants

Account ownership and timestamps are read-only; writable fields have explicit
allow-listing.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/serializers.py; profiles: base,full -->
```python
from rest_framework import serializers

from apps.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer[Customer]):
    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
```

##### Alternatives and trade-offs

Plain serializers make every field rule visible but duplicate valid model
metadata and need hand-written create and update methods.

##### Required tests

Test required name, email validation, length limits, partial updates, and
absence of the account field in input and output.

##### Related standards

- [Customer model](#srcappscustomermodelsmd)
- [Customer ViewSet](#srcappscustomerviewsmd)

### src/apps/customer/services.md

#### Transactional Customer import service

##### Purpose and when to use it

Use this service when a job or administrative endpoint must validate and create
several Customer records atomically.

##### When not to use it

Single-record API CRUD stays in the ModelViewSet and serializer.

##### Responsibilities and invariants

Every row is assigned the caller's account, all rows validate before the first
insert, and the transaction creates all records or none.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/services.py; profiles: base,full -->
```python
from collections.abc import Iterable, Mapping
from typing import Any

from django.db import transaction

from apps.account.models import Account
from apps.customer.models import Customer


@transaction.atomic
def import_customers(
    *,
    account: Account,
    rows: Iterable[Mapping[str, Any]],
) -> list[Customer]:
    customers = [
        Customer(
            account=account,
            name=str(row["name"]),
            email=str(row.get("email", "")),
            phone=str(row.get("phone", "")),
            notes=str(row.get("notes", "")),
        )
        for row in rows
    ]
    for customer in customers:
        customer.full_clean()
    return Customer.objects.bulk_create(customers)
```

##### Alternatives and trade-offs

Row-by-row creation gives individual signals and simpler attribution of a
database failure. Bulk insertion reduces queries but deliberately bypasses
`save()` and signals, so validation is explicit.

##### Required tests

Test one-account assignment, successful bulk creation, and complete rollback
when any row is invalid.

##### Related standards

- [Direct CRUD](#srcappscustomerviewsmd)
- [Service boundaries](#srcreadmemd)

### src/apps/customer/tests/README.md

#### Customer tests

The package covers direct CRUD, tenant isolation, filtering, pagination, and the
transactional import service.

<!-- artifact: src/apps/customer/tests/__init__.py; profiles: base,full -->
```python
"""Customer application tests."""
```

##### Related standards

- [Customer application](#srcappscustomerreadmemd)

### src/apps/customer/tests/helpers.md

#### Customer test helpers

##### Purpose and when to use it

Create a Customer through the public API when endpoint setup is not itself the
assertion.

##### When not to use it

Isolation tests should create cross-account records directly so ownership is
unambiguous.

##### Responsibilities and invariants

The helper fails immediately unless API creation succeeds.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/tests/helpers.py; profiles: base,full -->
```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.customer.models import Customer


def create_customer(
    *,
    client: APIClient,
    name: str = "Example Customer",
    email: str = "customer@example.com",
) -> Customer:
    response = client.post(
        reverse("api:customers:customer-list"),
        {"name": name, "email": email},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return Customer.objects.get(pk=response.json()["id"])
```

##### Alternatives and trade-offs

Direct ORM setup is faster and better when the API contract is unrelated to
the test.

##### Required tests

CRUD tests use this helper only after creation behavior has its own assertion.

##### Related standards

- [Customer endpoint tests](#srcappscustomerteststest_viewsmd)

### src/apps/customer/tests/test_services.md

#### Customer service tests

##### Purpose and when to use it

Verify the bulk import service's atomic validation and ownership rules.

##### When not to use it

Endpoint CRUD is covered separately.

##### Responsibilities and invariants

One invalid row prevents all inserts.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/tests/test_services.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.core.exceptions import ValidationError

from apps.customer.models import Customer
from apps.customer.services import import_customers


@pytest.mark.django_db
def test_import_customers_assigns_one_account(
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="import@example.com")
    rows = [
        {"name": "First", "email": "first@example.com"},
        {"name": "Second", "phone": "+1-555-0101"},
    ]

    # Act
    created = import_customers(
        account=user.account,
        rows=rows,
    )

    # Assert
    assert len(created) == 2
    assert Customer.objects.filter(account=user.account).count() == 2


@pytest.mark.django_db
def test_import_customers_validates_before_inserting(
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="rollback@example.com")
    rows = [
        {"name": "Valid"},
        {"name": "Invalid", "email": "not-an-email"},
    ]

    # Assert
    with pytest.raises(ValidationError):
        import_customers(
            account=user.account,
            rows=rows,
        )
    assert not Customer.objects.filter(account=user.account).exists()
```

##### Alternatives and trade-offs

Per-row error collection is friendlier for large imports but changes the
all-or-nothing contract and requires explicit result reporting.

##### Required tests

Run successful ownership and pre-insert validation cases.

##### Related standards

- [Import service](#srcappscustomerservicesmd)

### src/apps/customer/tests/test_views.md

#### Customer endpoint tests

##### Purpose and when to use it

Verify direct CRUD behavior and the non-negotiable account-isolation boundary.

##### When not to use it

Model and service rules with no HTTP behavior should use focused unit tests.

##### Responsibilities and invariants

Cross-account retrieve, update, and delete all return 404 and leave the target
unchanged.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/tests/test_views.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.customer.models import Customer


@pytest.mark.django_db
def test_customer_crud_is_direct_and_account_scoped(
    authenticated_client: APIClient,
    user: User,
) -> None:
    # Arrange
    list_url = reverse("api:customers:customer-list")
    payload = {
        "name": "Ada Example",
        "email": "ada@example.com",
        "phone": "+1-555-0100",
        "notes": "Prefers email",
    }

    # Act
    created = authenticated_client.post(
        list_url,
        payload,
    )
    customer = Customer.objects.get(pk=created.json()["id"])
    listing = authenticated_client.get(list_url, {"search": "Ada"})
    detail_url = reverse(
        "api:customers:customer-detail",
        kwargs={"pk": customer.pk},
    )
    updated = authenticated_client.patch(detail_url, {"notes": "Call first"})
    deleted = authenticated_client.delete(detail_url)

    # Assert
    assert created.status_code == status.HTTP_201_CREATED
    assert "account" not in created.json()
    assert customer.account == user.account
    assert listing.status_code == status.HTTP_200_OK
    assert [item["id"] for item in listing.json()["results"]] == [customer.pk]
    assert updated.status_code == status.HTTP_200_OK
    assert updated.json()["notes"] == "Call first"
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert not Customer.objects.filter(pk=customer.pk).exists()


@pytest.mark.django_db
def test_cross_account_objects_are_not_found_for_every_detail_action(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    actor = user_factory(email="actor@example.com")
    other = user_factory(email="other@example.com")
    target = Customer.objects.create(account=other.account, name="Private")
    api_client.force_authenticate(user=actor)
    detail_url = reverse(
        "api:customers:customer-detail",
        kwargs={"pk": target.pk},
    )

    # Act
    retrieved = api_client.get(detail_url)
    updated = api_client.patch(detail_url, {"name": "Changed"})
    deleted = api_client.delete(detail_url)
    target.refresh_from_db()

    # Assert
    assert retrieved.status_code == status.HTTP_404_NOT_FOUND
    assert updated.status_code == status.HTTP_404_NOT_FOUND
    assert deleted.status_code == status.HTTP_404_NOT_FOUND
    assert target.name == "Private"


@pytest.mark.django_db
def test_customer_endpoints_require_authentication(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:customers:customer-list")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"]


@pytest.mark.django_db
def test_inactive_account_is_denied(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="inactive@example.com", account_active=False)
    api_client.force_authenticate(user=user)
    url = reverse("api:customers:customer-list")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["details"]["detail"] == ("The account is not available.")
```

##### Alternatives and trade-offs

Permission-only tests can miss an unscoped queryset. Exercising each detail
action proves the object lookup itself is tenant-scoped.

##### Required tests

Keep CRUD, authentication, inactive-account, and three cross-account detail
actions mandatory.

##### Related standards

- [Customer ViewSet](#srcappscustomerviewsmd)
- [Account scoping](#srcappsapiviewsmd)

### src/apps/customer/urls.md

#### Customer routes

##### Purpose and when to use it

Expose the ViewSet's standard collection and detail actions.

##### When not to use it

Do not add action routes for workflows that belong to jobs or separate domain
resources.

##### Responsibilities and invariants

Routes are namespaced and have no duplicate API prefix.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/urls.py; profiles: base,full -->
```python
from rest_framework.routers import SimpleRouter

from apps.customer.views import CustomerViewSet

app_name = "customers"

router = SimpleRouter()
router.register("", CustomerViewSet, basename="customer")

urlpatterns = router.urls
```

##### Alternatives and trade-offs

Explicit `path()` declarations make each action visible but duplicate router
behavior for conventional CRUD.

##### Required tests

Reverse list and detail names and verify the `/api/v1/customers/` prefix.

##### Related standards

- [Customer ViewSet](#srcappscustomerviewsmd)
- [API composition](#srcappsapiurlsmd)

### src/apps/customer/views.md

#### Customer ViewSet

##### Purpose and when to use it

Provide conventional Customer CRUD with DRF's direct model primitives.

##### When not to use it

Do not override create, update, or destroy unless a transaction, effect, or
public contract requires behavior beyond serializer and model operations.

##### Responsibilities and invariants

The inherited queryset applies account scoping before every action.
`perform_create` assigns the trusted request account and never reads tenancy
from request data. The named scope adds a resource-specific limit on top of the
global sustained and burst limits.

##### Complete canonical artifact

<!-- artifact: src/apps/customer/views.py; profiles: base,full -->
```python
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.api.pagination import StableCursorPagination
from apps.api.views import AccountScopedViewSet
from apps.customer.models import Customer
from apps.customer.serializers import CustomerSerializer


class CustomerViewSet(AccountScopedViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    throttle_scope = "customers"
    pagination_class = StableCursorPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "email", "phone", "notes")
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-created_at", "-id")

    def perform_create(self, serializer: CustomerSerializer) -> None:
        serializer.save(account=self.get_account())
```

##### Alternatives and trade-offs

A hand-written APIView offers full control but repeats list, detail, validation,
and status-code behavior that ViewSets already make consistent.

##### Required tests

Exercise all actions and prove objects from another account return 404 for
retrieve, patch, and delete.

##### Related standards

- [Account scope base](#srcappsapiviewsmd)
- [Customer serializer](#srcappscustomerserializersmd)

### src/core/README.md

#### Core Process Configuration

- [settings package](#srccoresettingsreadmemd)
- [urls.py](#srccoreurlsmd)
- [asgi.py](#srccoreasgimd)
- [wsgi.py](#srccorewsgimd)
- [Celery application](#srccorecelerymd)

`settings` is an environment-driven package split by concern (see its
[README](#srccoresettingsreadmemd)). WSGI is the synchronous REST default; ASGI is
used by realtime profiles.

### src/core/__init__.md

#### Core Package

##### Purpose and when to use it

This retained module documents the Python package boundary. It is deliberately free of import-time side effects.

##### When not to use it

Do not initialize Celery, Sentry, Django, or network clients from a package initializer.

##### Responsibilities and invariants

Importing `core` is safe in management commands, test collection, WSGI, and ASGI processes.

##### Complete canonical artifact

<!-- artifact: src/core/__init__.py; profiles: base -->
```python
"""Process configuration for the Django service."""
```

##### Alternatives and trade-offs

Tasks import `core.celery` explicitly instead of using a compatibility alias here.

##### Required tests

Import `core` without configured external services.

##### Related standards

See [Celery](#srccorecelerymd) and [operations](#docsoperationsmd).

### src/core/asgi.md

#### ASGI Application

##### Purpose and when to use it

The base ASGI artifact supports Django's async request stack. Realtime profiles may replace it with Channels routing.

##### When not to use it

Prefer WSGI for a synchronous REST-only deployment when operational simplicity matters most.

##### Responsibilities and invariants

Initialize Django before importing any application code that may touch models.

##### Complete canonical artifact

<!-- artifact: src/core/asgi.py; profiles: base -->
```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
```

<!-- artifact: src/core/asgi.py; profiles: realtime-channels,realtime,full -->
```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django_application = get_asgi_application()

from apps.realtime.auth import JwtAuthMiddleware  # noqa: E402
from apps.realtime.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                JwtAuthMiddleware(
                    URLRouter(websocket_urlpatterns),
                )
            )
        ),
    }
)
```

##### Alternatives and trade-offs

Channels adds protocol routing and Redis only when WebSockets are required.

##### Required tests

Import the application and smoke-test it with an ASGI test client.

##### Related standards

See [SSE](#recipesssemd), [Channels](#recipeschannelsmd), and [operations](#docsoperationsmd).

### src/core/celery.md

#### Celery Application

##### Purpose and when to use it

Use this artifact whenever `celery-core` (or any module requiring it, such as `celery-django` or `chat-streaming`) is part of the resolved reconstruction.

##### When not to use it

Do not enqueue work that must commit atomically before the surrounding database transaction. Use `transaction.on_commit`.

##### Responsibilities and invariants

Configuration comes from Django settings, tasks are autodiscovered, and workers acknowledge tasks only after completion.

##### Complete canonical artifact

<!-- artifact: src/core/celery.py; profiles: celery-core,tasks,full -->
```python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("django_standard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-core -->
```toml
  "celery[redis]==5.6.3",
```

##### Alternatives and trade-offs

Use an in-process task only for best-effort non-durable work whose loss is acceptable.

##### Required tests

Run a worker smoke test and the retry/idempotency suite from the tasks recipe.

##### Related standards

See [the Celery module family](#recipesceleryreadmemd) and [chat streaming](#recipeschatmd).

### src/core/settings/README.md

#### Settings Package

##### Purpose and when to use it

Use this package, not a single module, as `DJANGO_SETTINGS_MODULE`. Each file
owns one concern; this index only aggregates them in a fixed, alphabetical
import order so every value is defined exactly once and easy to locate.

##### When not to use it

Do not add environment-conditional settings files (`local.py`,
`production.py`, ...). One environment-driven package serves every
environment; see [base](#srccoresettingsbasemd) for the production-safety checks that
replace per-environment modules.

##### Responsibilities and invariants

Every submodule may import concrete names from `.base` (for example
`SECRET_KEY`, `IS_PRODUCTION`, `module_exists`); nothing outside `base.py`
introduces new cross-module state. `INSTALLED_APPS` and `MIDDLEWARE` are
built once in `base.py` and only ever appended to or mutated in place by a
later submodule (see [cors](#srccoresettingscorsmd)), never rebuilt, so the aggregator's
import order does not change the final app or middleware list.

##### Complete canonical artifact

<!-- artifact: src/core/settings/__init__.py; profiles: base -->
```python
from .base import *  # noqa: F401,F403
from .celery import *  # noqa: F401,F403
from .channels import *  # noqa: F401,F403
from .cors import *  # noqa: F401,F403
from .database import *  # noqa: F401,F403
from .email import *  # noqa: F401,F403
from .jwt import *  # noqa: F401,F403
from .logging import *  # noqa: F401,F403
from .openai import *  # noqa: F401,F403
from .rest_framework import *  # noqa: F401,F403
from .security import *  # noqa: F401,F403
from .sentry import *  # noqa: F401,F403
from .storage import *  # noqa: F401,F403
```

##### Alternatives and trade-offs

A single flat `settings.py` has no import graph to reason about but grows
into one screen-scrolling file mixing unrelated concerns. Splitting by
concern costs one aggregator and a handful of small cross-imports from
`base.py`; `ty`/Ruff still resolve every name because each submodule exports
concrete top-level names, not a dynamic namespace.

##### Required tests

Import `core.settings` without configured external services, with every
optional dependency present, and with every optional dependency absent.
Confirm `python -c "from core.settings import INSTALLED_APPS"` includes
`corsheaders` exactly once.

##### Related standards

See [base](#srccoresettingsbasemd), [reconstruction](#docsreconstructionmd), and
[environment](#environmentmd).

### src/core/settings/base.md

#### Core Django Settings

##### Purpose and when to use it

Use this module for the settings package's shared foundation: paths, the
`module_exists` optional-dependency probe, the environment/secret/host
knobs every other submodule reads, installed apps, middleware, URLconf, and
templates.

##### When not to use it

Do not add a setting here that only one other submodule needs; give that
setting its own file and import the shared value from here instead.

##### Responsibilities and invariants

Local defaults are non-public and usable without external services.
Production configuration fails before Django starts when required security
values are absent. `INSTALLED_APPS` and `MIDDLEWARE` are built as lists so
later submodules (see [cors](#srccoresettingscorsmd)) can append or insert into them in
place.

Optional application discovery uses `module_exists`, the same pattern
[celery](#srccoresettingscelerymd), [channels](#srccoresettingschannelsmd), and [sentry](#srccoresettingssentrymd) use to
stay importable whether or not their package is part of the resolved
reconstruction.

##### Complete canonical artifact

<!-- artifact: src/core/settings/base.py; profiles: base -->
```python
from __future__ import annotations

import importlib.util
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BASE_DIR.parent


def module_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


ENVIRONMENT = config("ENVIRONMENT", default="local").strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG = config("DEBUG", default=False, cast=bool)

development_secret = "local-only-change-me-000000000000000000000000000000"
SECRET_KEY = config("SECRET_KEY", default=development_secret)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
DATABASE_URL = config("DATABASE_URL", default=None)

if IS_PRODUCTION:
    errors: list[str] = []
    if DEBUG:
        errors.append("DEBUG must be false")
    if development_secret == SECRET_KEY or len(SECRET_KEY) < 50:
        errors.append("SECRET_KEY must be a unique value of at least 50 characters")
    if not config("ALLOWED_HOSTS", default=""):
        errors.append("ALLOWED_HOSTS must be explicit")
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    if errors:
        raise ImproperlyConfigured("Invalid production settings: " + "; ".join(errors))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "apps.common",
    "apps.account",
    "apps.authentication",
    "apps.api",
    "apps.customer",
]

OPTIONAL_APPLICATIONS = (
    "apps.jobs",
    "apps.files",
    "apps.realtime",
    "apps.documents",
    "apps.membership",
)
for optional_application in OPTIONAL_APPLICATIONS:
    if module_exists(optional_application):
        INSTALLED_APPS.append(optional_application)

if module_exists("channels"):
    INSTALLED_APPS.append("channels")
if module_exists("django_celery_results"):
    INSTALLED_APPS.append("django_celery_results")
if module_exists("django_celery_beat"):
    INSTALLED_APPS.append("django_celery_beat")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.api.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "authentication.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_DIR / "media"

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
```

##### Alternatives and trade-offs

SQLite is a safe local convenience, not a substitute for PostgreSQL
integration tests; [database](#srccoresettingsdatabasemd) owns that decision. Dynamic
optional app discovery lets this module remain importable across profiles;
capability-specific behavior must still be explicitly enabled by its URLs
and workers.

##### Required tests

Test environment parsing, production failure cases, Django checks, deploy
checks, and settings import without optional dependencies.

##### Related standards

See [database](#srccoresettingsdatabasemd), [security](#srccoresettingssecuritymd),
[API design](#docsapi-designmd),
[security standards](#docssecuritymd), and
[environment](#environmentmd).

### src/core/settings/celery.md

#### Celery Settings

##### Purpose and when to use it

Use this module for the Celery app configuration consumed by
[`core.celery`](#srccorecelerymd): broker, result backend, and task
reliability flags.

##### When not to use it

Do not put task definitions or the `Celery()` app instance here; those
belong in `core.celery` and each app's `tasks.py`.

##### Responsibilities and invariants

Tasks acknowledge late and are rejected (requeued) on worker loss, so a
killed worker does not silently drop in-flight work.

##### Complete canonical artifact

<!-- artifact: src/core/settings/celery.py; profiles: base -->
```python
from decouple import config

from .base import TIME_ZONE

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="django-db")
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = TIME_ZONE
```

##### Required tests

Settings import without `django_celery_results`/`django_celery_beat`
installed; a task submitted against the configured broker is picked up by a
worker.

##### Related standards

See [base](#srccoresettingsbasemd), [core.celery](#srccorecelerymd), and
[celery recipes](#recipesceleryreadmemd).

### src/core/settings/channels.md

#### Channel Layer Settings

##### Purpose and when to use it

Use this module for the Redis URL shared by Celery's broker/cache use cases
and, when `channels_redis` is installed, the ASGI channel layer.

##### When not to use it

Do not configure `CHANNEL_LAYERS` unconditionally; a reconstruction that
excludes `realtime-channels` never installs `channels_redis`, and this
module must stay importable in that case.

##### Responsibilities and invariants

`CHANNEL_LAYERS` is only defined when `module_exists("channels_redis")` is
true, mirroring [sentry](#srccoresettingssentrymd)'s optional-dependency gate.

##### Complete canonical artifact

<!-- artifact: src/core/settings/channels.py; profiles: base -->
```python
from decouple import config

from .base import module_exists

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")
if module_exists("channels_redis"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
```

##### Required tests

Settings import without `channels_redis` installed; a WebSocket round trip
succeeds when it is installed.

##### Related standards

See [base](#srccoresettingsbasemd) and [channels](#recipeschannelsmd).

### src/core/settings/cors.md

#### Cross-Origin Requests

##### Purpose and when to use it

Use `django-cors-headers` to let a browser-based frontend on a different
origin call this API with credentials.

##### When not to use it

Do not widen `CORS_ALLOWED_ORIGINS` to `"*"` alongside
`CORS_ALLOW_CREDENTIALS`; browsers reject that combination and it is unsafe
for a cookie- or credentialed-header-bearing API regardless.

##### Responsibilities and invariants

`corsheaders` is appended to [base](#srccoresettingsbasemd)'s `INSTALLED_APPS` and its
middleware is inserted immediately before `CommonMiddleware`, matching the
package's own placement requirement. Allowed origins are explicit and
environment-driven; there is no default origin in a non-local environment.

##### Complete canonical artifact

<!-- artifact: src/core/settings/cors.py; profiles: base -->
```python
from decouple import Csv, config

from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.append("corsheaders")
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "corsheaders.middleware.CorsMiddleware",
)

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
```

##### Alternatives and trade-offs

`CORS_ALLOWED_ORIGINS` lists exact origins rather than using
`CORS_ALLOWED_ORIGIN_REGEXES`; a regex invites an accidentally permissive
pattern and this project's frontends are a small, known set.

##### Required tests

A preflight `OPTIONS` request from an allowed origin succeeds; one from an
unlisted origin is not granted `Access-Control-Allow-Origin`.

##### Related standards

See [base](#srccoresettingsbasemd), [security](#srccoresettingssecuritymd), and
[environment](#environmentmd).

### src/core/settings/database.md

#### Database Configuration

##### Purpose and when to use it

Use `database_config` to translate one `DATABASE_URL` into Django's
`DATABASES` shape, accepting SQLite or PostgreSQL.

##### When not to use it

Do not read individual `DB_*` variables; a single URL keeps local, test, and
production configuration in one value.

##### Responsibilities and invariants

An absent `DATABASE_URL` falls back to a local SQLite file, never to a
guessed PostgreSQL host. A malformed or unsupported scheme fails fast with
`ImproperlyConfigured` instead of producing a partially valid config.

##### Complete canonical artifact

<!-- artifact: src/core/settings/database.py; profiles: base -->
```python
from __future__ import annotations

from urllib.parse import parse_qsl, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

from .base import DATABASE_URL, PROJECT_DIR


def database_config(raw_url: str | None) -> dict[str, object]:
    if not raw_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": PROJECT_DIR / "db.sqlite3",
        }

    parsed = urlparse(raw_url)
    if parsed.scheme == "sqlite":
        if not parsed.path:
            raise ImproperlyConfigured("DATABASE_URL must include a SQLite path")
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": unquote(parsed.path),
        }
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_URL must use sqlite or postgresql")

    options = dict(parse_qsl(parsed.query))
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
        "CONN_MAX_AGE": 60,
        "OPTIONS": options,
    }


DATABASES = {"default": database_config(DATABASE_URL)}
```

##### Alternatives and trade-offs

SQLite is a safe local convenience, not a substitute for PostgreSQL
integration tests.

##### Required tests

Test SQLite fallback, a PostgreSQL URL with credentials and query options,
and rejection of an unsupported scheme.

##### Related standards

See [base](#srccoresettingsbasemd) and [testing](#docstestingmd).

### src/core/settings/email.md

#### Email Configuration

##### Purpose and when to use it

Use this module for the outbound email backend and default sender address.

##### When not to use it

Do not send email directly from views or services with a hardcoded backend;
read `EMAIL_BACKEND` so tests and local runs use the console backend
automatically.

##### Responsibilities and invariants

The default backend writes to the console, so no environment sends real
email without explicit configuration.

##### Complete canonical artifact

<!-- artifact: src/core/settings/email.py; profiles: base -->
```python
from decouple import config

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@localhost")
```

##### Required tests

Test that the default backend is the console backend and that outgoing
messages use `DEFAULT_FROM_EMAIL`.

##### Related standards

See [base](#srccoresettingsbasemd).

### src/core/settings/jwt.md

#### JWT Configuration

##### Purpose and when to use it

Use this module for `djangorestframework-simplejwt`'s token lifetimes and
rotation behavior.

##### When not to use it

Do not lengthen `ACCESS_TOKEN_LIFETIME` to avoid refresh calls; short-lived
access tokens limit the blast radius of a leaked token.

##### Responsibilities and invariants

Refresh tokens rotate and are blacklisted after rotation, so a stolen
refresh token stops working the next time the legitimate client refreshes.

##### Complete canonical artifact

<!-- artifact: src/core/settings/jwt.py; profiles: base -->
```python
from datetime import timedelta

from .base import SECRET_KEY

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

##### Alternatives and trade-offs

Signing with `SECRET_KEY` avoids a second secret to rotate; a dedicated JWT
signing key would let JWT rotation happen independently of the Django
session/CSRF secret at the cost of one more required production variable.

##### Required tests

Test access token expiry, refresh rotation, and blacklist rejection of a
reused refresh token.

##### Related standards

See [base](#srccoresettingsbasemd), [rest_framework](#srccoresettingsrest-frameworkmd), and
[authentication](#srcappsauthenticationreadmemd).

### src/core/settings/logging.md

#### Logging Configuration

##### Purpose and when to use it

Use this module for the process-wide `LOGGING` dict shared by the web,
worker, and management-command processes.

##### When not to use it

Do not configure a logger inside application code; add it to this dict so
every process shares one format and one request-ID filter.

##### Responsibilities and invariants

Every log line carries `request_id` through
[`RequestIDLogFilter`](#srcappsapimiddlewaremd), even for log calls
issued outside of a request-bound view.

##### Complete canonical artifact

<!-- artifact: src/core/settings/logging.py; profiles: base -->
```python
from decouple import config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": ("{asctime} {levelname} {name} request_id={request_id} {message}"),
            "style": "{",
        }
    },
    "filters": {
        "request_id": {
            "()": "apps.api.middleware.RequestIDLogFilter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_id"],
        }
    },
    "root": {"handlers": ["console"], "level": config("LOG_LEVEL", default="INFO")},
}
```

##### Required tests

Confirm a log line emitted during a request includes that request's
`request_id`.

##### Related standards

See [base](#srccoresettingsbasemd) and [middleware](#srcappsapimiddlewaremd).

### src/core/settings/openai.md

#### OpenAI Settings

##### Purpose and when to use it

Use this module for the OpenAI credentials and model names consumed by the
[vector/AI recipes](#recipesvectormd).

##### When not to use it

Do not read `OPENAI_API_KEY` directly in application code; import from this
module so tests can override it in one place.

##### Responsibilities and invariants

`OPENAI_SAFETY_IDENTIFIER_SECRET` falls back to `SECRET_KEY` so a
reconstruction that never sets it still has a stable, non-guessable per-
deployment value to derive a safety identifier from.

##### Complete canonical artifact

<!-- artifact: src/core/settings/openai.py; profiles: base -->
```python
from decouple import config

from .base import SECRET_KEY

OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-5.6-sol")
OPENAI_EMBEDDING_MODEL = config(
    "OPENAI_EMBEDDING_MODEL",
    default="text-embedding-3-small",
)
OPENAI_EMBEDDING_DIMENSIONS = config("OPENAI_EMBEDDING_DIMENSIONS", default=1536, cast=int)
OPENAI_SAFETY_IDENTIFIER_SECRET = config(
    "OPENAI_SAFETY_IDENTIFIER_SECRET",
    default=SECRET_KEY,
)
```

##### Required tests

Settings import with `OPENAI_API_KEY` unset; embedding calls use
`OPENAI_EMBEDDING_DIMENSIONS` to validate vector width.

##### Related standards

See [base](#srccoresettingsbasemd) and [vector](#recipesvectormd).

### src/core/settings/rest-framework.md

#### Django REST Framework Configuration

##### Purpose and when to use it

Use this module for every DRF-wide default: authentication, permissions,
throttling, filtering, pagination, and error handling.

##### When not to use it

Do not set per-view DRF options here; only cross-cutting defaults belong in
this module, and views override them explicitly.

##### Responsibilities and invariants

API throttles combine anonymous, authenticated-user, burst, and
endpoint-scoped limits, each independently overridable through its own
environment variable.

##### Complete canonical artifact

<!-- artifact: src/core/settings/rest_framework.py; profiles: base -->
```python
from decouple import config

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "apps.api.throttling.BurstRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("API_THROTTLE_ANON", default="100/hour"),
        "user": config("API_THROTTLE_USER", default="2000/day"),
        "burst": config("API_THROTTLE_BURST", default="60/minute"),
        "registration": config("API_THROTTLE_REGISTRATION", default="5/hour"),
        "token": config("API_THROTTLE_TOKEN", default="10/minute"),
        "token_refresh": config("API_THROTTLE_TOKEN_REFRESH", default="30/minute"),
        "token_verify": config("API_THROTTLE_TOKEN_VERIFY", default="60/minute"),
        "customers": config("API_THROTTLE_CUSTOMERS", default="600/hour"),
    },
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.api.pagination.StableCursorPagination",
    "EXCEPTION_HANDLER": "apps.api.exceptions.api_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}
```

##### Alternatives and trade-offs

DRF's application throttles are cache-backed fairness controls, not a
denial-of-service boundary. Django's default local-memory cache is
sufficient for deterministic local examples but counts separately in every
process. Production deployments must use a shared cache for consistent
application limits and enforce authoritative abuse controls at the trusted
reverse proxy, API gateway, or edge.

##### Required tests

Test throttle rejection per scope and the exception handler's error shape.

##### Related standards

See [base](#srccoresettingsbasemd), [jwt](#srccoresettingsjwtmd), and
[API design](#docsapi-designmd).

### src/core/settings/security.md

#### Security Headers and Cookies

##### Purpose and when to use it

Use this module for CSRF origins, cookie flags, and the HSTS/TLS-related
security headers that must differ between local and production.

##### When not to use it

Do not toggle these values per view; they are process-wide and derived once
from `IS_PRODUCTION`.

##### Responsibilities and invariants

Every cookie- and transport-security flag that must be `True` in production
and may be relaxed locally derives from the single `IS_PRODUCTION` value in
[base](#srccoresettingsbasemd), so there is one place that can get this wrong instead of
eight.

##### Complete canonical artifact

<!-- artifact: src/core/settings/security.py; profiles: base -->
```python
from decouple import Csv, config

from .base import IS_PRODUCTION

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_HSTS_SECONDS = 31_536_000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
```

##### Alternatives and trade-offs

`SECURE_PROXY_SSL_HEADER` trusts `X-Forwarded-Proto` unconditionally; this
is only safe behind a reverse proxy that strips client-supplied forwarding
headers, per [security](#docssecuritymd).

##### Required tests

Test that production settings enable every secure flag and that local
settings do not require TLS.

##### Related standards

See [base](#srccoresettingsbasemd), [cors](#srccoresettingscorsmd), and
[security](#docssecuritymd).

### src/core/settings/sentry.md

#### Sentry Initialization

##### Purpose and when to use it

Use this module to initialize `sentry_sdk` when the
[`sentry-django`](#recipessentrysentry-djangomd) module is part
of the resolved reconstruction.

##### When not to use it

Do not import `sentry_sdk` unconditionally; a base reconstruction that
excludes the `sentry-django` module never installs the package.

##### Responsibilities and invariants

Initialization is gated by `module_exists("sentry_sdk")`, so this module
stays importable whether or not `sentry-sdk` is installed. `SENTRY_DSN`
empty is a valid, fully local configuration: the SDK is imported but never
initialized.

##### Complete canonical artifact

<!-- artifact: src/core/settings/sentry.py; profiles: base -->
```python
from decouple import config

from .base import ENVIRONMENT, module_exists

if module_exists("sentry_sdk"):
    import sentry_sdk

    SENTRY_DSN = config("SENTRY_DSN", default="")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            send_default_pii=False,
            traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=0, cast=float),
        )
```

##### Required tests

Settings import without `sentry-sdk` installed; settings import with it
installed and `SENTRY_DSN` unset does not call `sentry_sdk.init`.

##### Related standards

See [base](#srccoresettingsbasemd) and [sentry](#recipessentryreadmemd).

### src/core/settings/storage.md

#### Object Storage Settings

##### Purpose and when to use it

Use this module for the S3-compatible credentials and limits consumed by
[storage](#recipesstoragestorage-djangomd).

##### When not to use it

Do not read these values directly in application code; go through the
storage backend so a swapped provider only changes this module.

##### Responsibilities and invariants

A separate public endpoint is supported for setups where the
application-facing S3 endpoint (e.g. an internal MinIO host) differs from
the one used to build public URLs; it falls back to the private endpoint
when unset.

##### Complete canonical artifact

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

##### Required tests

Settings import with credentials unset; a presigned URL uses
`AWS_S3_PUBLIC_ENDPOINT_URL` when it differs from `AWS_S3_ENDPOINT_URL`.

##### Related standards

See [base](#srccoresettingsbasemd) and [storage](#recipesstoragestorage-djangomd).

### src/core/urls.md

#### Root URL Configuration

##### Purpose and when to use it

This is the stable process-level URL boundary.

##### When not to use it

Application endpoints belong in their app URL modules.

##### Responsibilities and invariants

Admin is isolated under `/admin/`; versioned JSON APIs are under `/api/v1/`.

##### Complete canonical artifact

<!-- artifact: src/core/urls.py; profiles: base -->
```python
from importlib.util import find_spec

from django.contrib import admin
from django.urls import include, path


def module_exists(name: str) -> bool:
    try:
        return find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
]

OPTIONAL_URLS = (
    ("api/v1/jobs/", "apps.jobs.urls"),
    ("api/v1/files/", "apps.files.urls"),
    ("api/v1/events/", "apps.realtime.urls"),
)
for prefix, module in OPTIONAL_URLS:
    if module_exists(module):
        urlpatterns.append(path(prefix, include(module)))
```

##### Alternatives and trade-offs

Host-based routing is appropriate only when separate domains have distinct security boundaries.

##### Required tests

Reverse every named health, auth, and Customer route.

##### Related standards

See [API URLs](#srcappsapiurlsmd).

### src/core/wsgi.md

#### WSGI Application

##### Purpose and when to use it

Use Gunicorn with WSGI for synchronous REST deployments.

##### When not to use it

Use ASGI when the service owns SSE or WebSocket connections.

##### Responsibilities and invariants

This module performs no configuration beyond choosing `core.settings`.

##### Complete canonical artifact

<!-- artifact: src/core/wsgi.py; profiles: base -->
```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
```

##### Alternatives and trade-offs

See the deployment comparison before mixing WSGI and ASGI worker pools.

##### Required tests

Import `application` and smoke-test one request through Gunicorn.

##### Related standards

See [ASGI](#srccoreasgimd) and [operations](#docsoperationsmd).

### src/manage.md

#### Django Management Entry Point

##### Purpose and when to use it

Use this artifact for local management commands, migration jobs, checks, and the development server.

##### When not to use it

Production web processes should invoke Gunicorn or Daphne directly.

##### Responsibilities and invariants

The entry point sets only the settings module and delegates to Django. Configuration belongs in the environment and `core.settings`.

##### Complete canonical artifact

<!-- artifact: src/manage.py; profiles: base -->
```python
#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

##### Alternatives and trade-offs

Framework-specific wrappers add no value here. Keep this file conventional.

##### Required tests

Run `python src/manage.py check` and the migration drift check.

##### Related standards

See [settings](#srccoresettingsreadmemd) and [operations](#docsoperationsmd).

### tests/conftest.md

#### System Test Fixtures

##### Purpose and when to use it

System tests consume a running server URL explicitly; they never start infrastructure during import.

##### Complete canonical artifact

<!-- artifact: tests/conftest.py; profiles: base -->
```python
import os

import pytest


@pytest.fixture(scope="session")
def live_server_url() -> str:
    configured = os.getenv("LIVE_SERVER_URL")
    if not configured:
        pytest.skip("LIVE_SERVER_URL is required for live-server smoke tests")
    return configured.rstrip("/")
```

##### Required tests

Collection succeeds without a live server; marked smoke tests fail clearly when it is unavailable.

### tests/test_healthcheck.md

#### Live Health Smoke Test

##### Purpose and when to use it

This optional system test checks a process already running through its public HTTP boundary.

##### When not to use it

The ordinary unit suite uses Django's test client and requires no live process.

##### Complete canonical artifact

<!-- artifact: tests/test_healthcheck.py; profiles: base -->
```python
import urllib.request

import pytest


@pytest.mark.integration
def test_live_health_endpoint(live_server_url: str) -> None:
    # Arrange
    url = f"{live_server_url}/api/v1/live/"

    # Act
    with urllib.request.urlopen(
        url,
        timeout=3,
    ) as response:
        status_code = response.status
        content_type = response.headers["Content-Type"]

    # Assert
    assert status_code == 200
    assert content_type.startswith("application/json")
```

##### Required tests

Run this test only after the chosen WSGI or ASGI server reports ready.

### scripts/beat.md

#### Celery Beat Entrypoint

##### Purpose and when to use it

Use this entrypoint whenever `celery-beat` is part of the resolved
reconstruction, alongside at least one worker. Beat itself never executes
task bodies; it only enqueues due tasks read from the database-backed
schedule described in [celery-beat](#recipescelerycelery-beatmd).

##### When not to use it

Do not run more than one beat process against the same schedule; duplicate
beats double-enqueue periodic tasks. `DatabaseScheduler` polls PostgreSQL, not
a file, so no `celerybeat-schedule` file needs a shared volume.

##### Complete canonical artifact

<!-- artifact: scripts/beat.sh; profiles: celery-beat,tasks,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec celery -A core.celery:app beat \
  --loglevel="${CELERY_LOG_LEVEL:-INFO}" \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

##### Responsibilities and invariants

Signals reach Celery. The scheduler is always `DatabaseScheduler`, so a
schedule change only requires updating `PeriodicTask` rows, not a redeploy.

##### Alternatives and trade-offs

The default file-backed `PersistentScheduler` needs a persistent volume and
loses schedule edits made outside the process. `DatabaseScheduler` trades a
small per-tick database read for operator-editable, code-free scheduling.

##### Required tests

Check shell syntax and run the `sync_periodic_tasks` idempotency test from
[celery-beat](#recipescelerycelery-beatmd).

##### Related standards

See [the Celery module family](#recipesceleryreadmemd) and
[the Celery worker entrypoint](#scriptsworkermd).

### scripts/channels-worker.md

#### Channels Background Worker

##### Purpose and when to use it

Use `runworker` only for explicitly routed Channels background messages; it does not replace Celery durability. Requires `realtime-channels` — SSE has no consumer-routed background messages.

##### Complete canonical artifact

<!-- artifact: scripts/channels-worker.sh; profiles: realtime-channels,realtime,full -->
```sh
#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
  echo "at least one channel name is required" >&2
  exit 2
fi

exec python src/manage.py runworker "$@"
```

##### Responsibilities and invariants

The caller supplies an allowlisted channel name. Durable jobs remain in Celery.

##### Required tests

Check shell syntax and route one test message to an explicit channel.

### scripts/channels.md

#### Daphne ASGI Entrypoint

##### Purpose and when to use it

Use Daphne for HTTP, SSE, and WebSockets whenever `realtime-sse` or `realtime-channels` is part of the resolved reconstruction — this entrypoint works for either alone.

##### Complete canonical artifact

<!-- artifact: scripts/channels.sh; profiles: realtime-sse,realtime-channels,realtime,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec daphne \
  --bind "${DAPHNE_BIND:-0.0.0.0}" \
  --port "${DAPHNE_PORT:-8000}" \
  core.asgi:application
```

##### Responsibilities and invariants

TLS and request limits belong at the trusted reverse proxy.

##### Required tests

Check shell syntax and smoke-test HTTP plus a WebSocket handshake.

### scripts/webserver.md

#### WSGI Web Entrypoint

##### Purpose and when to use it

Use this process entrypoint in a synchronous REST container.

##### Complete canonical artifact

<!-- artifact: scripts/webserver.sh; profiles: base -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec gunicorn \
  --chdir "$project_dir/src" \
  --config "$project_dir/gunicorn.conf.py" \
  core.wsgi:application
```

##### Responsibilities and invariants

Migrations run as a separate release job. `exec` ensures signals reach Gunicorn.

##### Required tests

Check shell syntax and graceful container termination.

### scripts/worker.md

#### Celery Worker Entrypoint

##### Purpose and when to use it

Use this entrypoint whenever `celery-core` is part of the resolved reconstruction.

##### Complete canonical artifact

<!-- artifact: scripts/worker.sh; profiles: celery-core,tasks,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec celery -A core.celery:app worker \
  --loglevel="${CELERY_LOG_LEVEL:-INFO}" \
  --concurrency="${CELERY_CONCURRENCY:-2}"
```

##### Responsibilities and invariants

Signals reach Celery and worker concurrency has a conservative default.

##### Required tests

Check shell syntax and run the task worker smoke test.

##### Related standards

See [the Celery module family](#recipesceleryreadmemd) and
[the Celery beat entrypoint](#scriptsbeatmd).

### .vscode/launch.md

#### VS Code Launch Configuration

##### Purpose and when to use it

Use this optional configuration to debug Django locally through the reconstructed virtual environment.

##### Complete canonical artifact

<!-- artifact: .vscode/launch.json; profiles: base -->
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django API",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/manage.py",
      "args": ["runserver", "0.0.0.0:8000"],
      "django": true,
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

##### Required tests

Debug configuration must not contain credentials or override production flags.

### .vscode/settings.md

#### VS Code Settings

##### Purpose and when to use it

These optional editor settings align save-time behavior with repository tools.

##### Complete canonical artifact

<!-- artifact: .vscode/settings.json; profiles: base -->
```json
{
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["."],
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

##### Required tests

Workspace settings must remain optional; command-line checks define correctness.

### recipes/README.md

#### Optional Recipes

Recipes inherit the base project and add one coherent capability, broken
into small composable **modules** with explicit dependency edges (see
[reconstruction](#docsreconstructionmd) for how requests resolve):

- [Celery](#recipesceleryreadmemd) — `celery-core`, `celery-redis-broker`,
  `celery-postgres-results`, `celery-django`, `celery-beat`.
- [Storage](#recipesstoragestorage-s3-coremd) — `storage-s3-core`,
  [`storage-django`](#recipesstoragestorage-djangomd).
- Realtime — [SSE](#recipesssemd) (`realtime-sse`) and [Channels](#recipeschannelsmd)
  (`realtime-channels`), independent of each other.
- Vector/AI — [pgvector](#recipesvectormd) (`vector-pgvector`),
  [OpenAI and Deep Agents](#recipesopenai-deep-agentsmd) (`vector-ai-openai`), and
  [chat streaming](#recipeschatmd) (`chat-streaming`).
- [Sentry](#recipessentryreadmemd) — `sentry-python`, `sentry-django`.
- [Advanced tenancy](#recipestenancymd) — `tenancy-advanced`.
- [Deployment comparison](#recipesdeploymentmd) — not a module; documents WSGI vs.
  ASGI trade-offs across every module combination.

The legacy `tasks`, `storage`, `realtime`, `vector-ai`, and `full` names
still work as aliases that expand to a fixed module set — see the alias
table in [reconstruction](#docsreconstructionmd). Request individual
modules directly (`--modules celery-django,sentry-django`) for combinations
the six original profiles could never express. Choose modules because the
product needs them; `full` is an integration teaching project, not a
recommendation to install everything.

Each module states when the added infrastructure is justified, owns only
its feature-level canonical artifacts, and lists the integration and
failure cases that must be tested. Project aggregators such as settings,
URLs, dependency locks, Compose, and core ASGI/Celery entry points remain
owned by their top-level standards so modules cannot silently overwrite one
another.

### recipes/celery/README.md

#### Celery

Durable background work, split into composable modules along the same
edges [`docs/reconstruction.md`](#docsreconstructionmd) resolves:

- [`celery-postgres-results`](#recipescelerycelery-postgres-resultsmd) — the durable
  `Job` model, its read-only DRF API, and `django-celery-results`. Requires
  only `celery-core` (the project Celery app at
  [`src/core/celery.md`](#srccorecelerymd)).
- [`celery-django`](#recipescelerycelery-djangomd) — task publication and status
  transitions (`create_job`, `claim_job`, `run_job`). Requires
  `celery-postgres-results`, because every operation reads or writes the
  `Job` row that module owns.
- [`celery-beat`](#recipescelerycelery-beatmd) — database-backed periodic scheduling
  (`sync_periodic_tasks`, `DatabaseScheduler`). Requires `celery-django`.
- [`celery-redis-broker`](#recipescelerycelery-redis-brokermd) — broker/result-backend
  configuration notes. Requires only `celery-core`; owns no artifacts of its
  own because the broker settings are aggregator-owned (see
  [settings](#srccoresettingsreadmemd), [environment](#environmentmd)).

Requesting `celery-django` alone pulls in `celery-postgres-results`
transitively (and `celery-core` through it) but not `celery-beat` — no
periodic scheduling is materialized unless asked for. The legacy `tasks`
alias still resolves to all five.

##### Related standards

See [the Celery application](#srccorecelerymd),
[the worker entrypoint](#scriptsworkermd),
[the beat entrypoint](#scriptsbeatmd), and
[chat streaming](#recipeschatmd), which uses `celery-core` directly without any
of these Job-model-backed modules.

### recipes/celery/celery-beat.md

#### Celery Beat — Database-Backed Scheduling

##### Purpose and when to use it

Use this module when periodic work is needed on top of
[`celery-django`](#recipescelerycelery-djangomd)'s task publication. The schedule lives in
PostgreSQL (`django_celery_beat`'s `DatabaseScheduler`), not in code, so
operators can change cadence without a deploy. `sync_periodic_tasks` seeds
and updates that schedule idempotently and runs as a release step alongside
migrations. Requires `celery-django`.

##### When not to use it

Do not run more than one beat process against the same schedule; duplicate
beats double-enqueue periodic tasks (enforced operationally, not by this
module).

##### Responsibilities and invariants

`sync_periodic_tasks` is idempotent: running it repeatedly updates the same
`PeriodicTask` row rather than creating duplicates.

##### Complete canonical artifacts

<!-- artifact: src/apps/jobs/management/commands/sync_periodic_tasks.py; profiles: celery-beat,tasks,full -->
```python
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create or update the database-backed Celery beat schedule."

    def handle(self, *args: Any, **options: Any) -> None:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )
        _, created = PeriodicTask.objects.update_or_create(
            name="purge-stale-jobs",
            defaults={
                "task": "apps.jobs.tasks.purge_stale_jobs",
                "interval": schedule,
                "crontab": None,
                "enabled": True,
            },
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(f"{verb} periodic task 'purge-stale-jobs'.")
```

<!-- artifact: src/apps/jobs/tests/test_jobs_beat.py; profiles: celery-beat,tasks,full -->
```python
import pytest
from django.core.management import call_command
from django_celery_beat.models import PeriodicTask


@pytest.mark.django_db
def test_sync_periodic_tasks_is_idempotent() -> None:
    # Act
    call_command("sync_periodic_tasks")
    call_command("sync_periodic_tasks")

    # Assert
    task = PeriodicTask.objects.get(name="purge-stale-jobs")
    assert task.task == "apps.jobs.tasks.purge_stale_jobs"
    assert task.enabled is True
    assert PeriodicTask.objects.filter(name="purge-stale-jobs").count() == 1
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-beat -->
```toml
  "django-celery-beat==2.9.0",
```

##### Alternatives and trade-offs

The default file-backed `PersistentScheduler` needs a persistent volume and
loses schedule edits made outside the process. `DatabaseScheduler` trades a
small per-tick database read for operator-editable, code-free scheduling.

##### Required tests

Cover retention deletion boundaries (in
[celery-django](#recipescelerycelery-djangomd)) and `sync_periodic_tasks` idempotency
(here).

##### Related standards

See [celery-django](#recipescelerycelery-djangomd), [the beat entrypoint](#scriptsbeatmd),
and [the Celery module family](#recipesceleryreadmemd).

### recipes/celery/celery-django.md

#### Celery Task Publication and Status Transitions

##### Purpose and when to use it

Use this module when work must survive a web request, run on a schedule, or
retry after a transient dependency failure. It publishes and executes the
Celery task that drives a [`celery-postgres-results`](#recipescelerycelery-postgres-resultsmd)
`Job` through its status transitions. Requires `celery-postgres-results`.

##### When not to use it

Do not enqueue work that must commit atomically inside the current request.
Use `transaction.on_commit` when a task depends on newly committed rows. Do
not retry validation or authorization failures.

##### Responsibilities and invariants

- Task publication happens only after the creating transaction commits.
- Workers claim a pending job with a row lock.
- Retriable failures return the job to `pending`; terminal failures are
  recorded without leaking secrets.
- Celery retries and task redelivery may run the same task more than once,
  so effects use their own durable idempotency key.
- Account-scoped periodic jobs are created through the same service used by
  request handlers. System-wide maintenance tasks, such as retention
  sweeps, may run directly since they have no owning account.

##### Complete canonical artifacts

<!-- artifact: src/apps/jobs/services.py; profiles: celery-django,tasks,full -->
```python
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.account.models import Account
from apps.jobs.models import Job


@transaction.atomic
def create_job(
    *,
    account: Account,
    kind: str,
    idempotency_key: str,
    enqueue: Callable[[str], Any],
) -> tuple[Job, bool]:
    job, created = Job.objects.get_or_create(
        account=account,
        idempotency_key=idempotency_key,
        defaults={"kind": kind},
    )
    if created:
        transaction.on_commit(lambda: enqueue(str(job.pk)))
    return job, created


@transaction.atomic
def claim_job(*, job_id: str) -> Job | None:
    job = Job.objects.select_for_update().filter(pk=job_id).first()
    if job is None or job.status != Job.Status.PENDING:
        return None
    job.status = Job.Status.RUNNING
    job.attempts += 1
    job.started_at = timezone.now()
    job.error_code = ""
    job.save(update_fields=("status", "attempts", "started_at", "error_code", "updated_at"))
    return job


@transaction.atomic
def mark_job_succeeded(*, job_id: str, result: dict[str, object]) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(
        status=Job.Status.SUCCEEDED,
        result=result,
        finished_at=timezone.now(),
        error_code="",
    )


@transaction.atomic
def mark_job_pending_for_retry(*, job_id: str) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(status=Job.Status.PENDING, error_code="temporary_dependency_failure")


@transaction.atomic
def mark_job_failed(*, job_id: str, error_code: str) -> None:
    Job.objects.select_for_update().filter(
        pk=job_id,
        status=Job.Status.RUNNING,
    ).update(
        status=Job.Status.FAILED,
        error_code=error_code,
        finished_at=timezone.now(),
    )


def purge_finished_jobs(*, older_than: timedelta) -> int:
    cutoff = timezone.now() - older_than
    deleted, _ = Job.objects.filter(
        status__in=(Job.Status.SUCCEEDED, Job.Status.FAILED),
        finished_at__lt=cutoff,
    ).delete()
    return deleted
```

<!-- artifact: src/apps/jobs/tasks.py; profiles: celery-django,tasks,full -->
```python
from __future__ import annotations

from datetime import timedelta
from typing import Any

import httpx
from celery import shared_task

from apps.jobs.services import (
    claim_job,
    mark_job_failed,
    mark_job_pending_for_retry,
    mark_job_succeeded,
    purge_finished_jobs,
)


def perform_job_effect(*, job_id: str) -> dict[str, object]:
    return {"job_id": job_id, "processed": True}


@shared_task(
    bind=True,
    autoretry_for=(),
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=5,
)
def run_job(self: Any, job_id: str) -> None:
    job = claim_job(job_id=job_id)
    if job is None:
        return

    try:
        result = perform_job_effect(job_id=str(job.pk))
    except (httpx.TimeoutException, httpx.NetworkError) as error:
        mark_job_pending_for_retry(job_id=str(job.pk))
        countdown = min(300, 2**job.attempts)
        raise self.retry(exc=error, countdown=countdown) from error
    except Exception:
        mark_job_failed(job_id=str(job.pk), error_code="job_execution_failed")
        raise
    else:
        mark_job_succeeded(job_id=str(job.pk), result=result)


@shared_task
def purge_stale_jobs() -> int:
    return purge_finished_jobs(older_than=timedelta(days=30))
```

<!-- artifact: src/apps/jobs/tests/test_jobs.py; profiles: celery-django,tasks,full -->
```python
from datetime import timedelta

import pytest
from celery.exceptions import Retry
from django.db import transaction
from django.utils import timezone

from apps.account.models import Account
from apps.authentication.models import User
from apps.jobs.models import Job
from apps.jobs.services import create_job, purge_finished_jobs
from apps.jobs.tasks import purge_stale_jobs, run_job


@pytest.mark.django_db(transaction=True)
def test_create_job_is_idempotent_and_publishes_after_commit() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    published: list[str] = []

    # Act
    with transaction.atomic():
        first, first_created = create_job(
            account=account,
            kind="customer-export",
            idempotency_key="export-2026-07",
            enqueue=published.append,
        )
        second, second_created = create_job(
            account=account,
            kind="customer-export",
            idempotency_key="export-2026-07",
            enqueue=published.append,
        )
        published_before_commit = list(published)

    # Assert
    assert published_before_commit == []
    assert first == second
    assert first_created is True
    assert second_created is False
    assert published == [str(first.pk)]


@pytest.mark.django_db
def test_completed_task_is_safe_to_redeliver() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    job = Job.objects.create(
        account=account,
        kind="customer-export",
        idempotency_key="one-delivery",
    )

    # Act
    run_job.run(str(job.pk))
    run_job.run(str(job.pk))
    job.refresh_from_db()

    # Assert
    assert job.status == Job.Status.SUCCEEDED
    assert job.attempts == 1


@pytest.mark.django_db
def test_transient_failure_returns_job_to_pending(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    job = Job.objects.create(account=account, kind="sync", idempotency_key="retry")

    def fail(*, job_id: str) -> dict[str, object]:
        import httpx

        raise httpx.ConnectError("temporary")

    monkeypatch.setattr("apps.jobs.tasks.perform_job_effect", fail)

    # Assert
    with pytest.raises(Retry):
        run_job.apply(args=(str(job.pk),), throw=True)
    assert (persisted_job := Job.objects.get(pk=job.pk)).status == Job.Status.PENDING
    assert persisted_job.error_code == "temporary_dependency_failure"


@pytest.mark.django_db
def test_purge_stale_jobs_deletes_only_old_terminal_jobs() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    stale = Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="stale",
        status=Job.Status.SUCCEEDED,
        finished_at=timezone.now() - timedelta(days=31),
    )
    recent = Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="recent",
        status=Job.Status.SUCCEEDED,
        finished_at=timezone.now(),
    )
    pending = Job.objects.create(account=account, kind="export", idempotency_key="pending")

    # Act
    deleted = purge_stale_jobs.run()

    # Assert
    assert deleted == 1
    assert not Job.objects.filter(pk=stale.pk).exists()
    assert Job.objects.filter(pk=recent.pk).exists()
    assert Job.objects.filter(pk=pending.pk).exists()


@pytest.mark.django_db
def test_purge_finished_jobs_returns_deleted_count() -> None:
    # Arrange
    user = User.objects.create_user(email="jobs@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    Job.objects.create(
        account=account,
        kind="export",
        idempotency_key="stale",
        status=Job.Status.FAILED,
        finished_at=timezone.now() - timedelta(days=60),
    )

    # Act
    deleted = purge_finished_jobs(older_than=timedelta(days=30))

    # Assert
    assert deleted == 1
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-django -->
```toml
  "httpx==0.28.1",
```

##### Alternatives and trade-offs

A database-backed task queue reduces infrastructure but has a different
throughput and scheduling profile than Celery/Redis.

##### Required tests

Run a worker against Redis and PostgreSQL. Cover transaction rollback
without publication, duplicate HTTP requests, worker redelivery, retry
exhaustion, terminal failure sanitization, account-scoped polling, and
result expiration. Run worker tests with eager mode disabled for at least
one integration suite.

##### Related standards

See [celery-postgres-results](#recipescelerycelery-postgres-resultsmd) (owns the `Job`
model this module transitions), [celery-beat](#recipescelerycelery-beatmd), and
[the Celery module family](#recipesceleryreadmemd).

### recipes/celery/celery-postgres-results.md

#### Celery Postgres-Backed Job Status

##### Purpose and when to use it

Use this module for a durable, queryable record of work: a `Job` row is
created before any task publishes, and PostgreSQL — not the Celery result
backend — remains the source of truth for user-visible status. Requires
`celery-core` (see [the Celery application](#srccorecelerymd)).

##### When not to use it

Do not use a Celery result backend as the product record of execution.
Results remain operational metadata; this module's `Job` row is the API
contract.

##### Responsibilities and invariants

- A caller-provided idempotency key identifies one logical job per account.
- `Job.status` transitions are the durable record; `django_celery_results`
  stores Celery's own operational result data alongside it.
- Retrieval is read-only and account-scoped, matching every other tenant-owned
  resource in this handbook.

##### Complete canonical artifacts

<!-- artifact: src/apps/jobs/apps.py; profiles: celery-postgres-results,tasks,full -->
```python
from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jobs"
```

<!-- artifact: src/apps/jobs/models.py; profiles: celery-postgres-results,tasks,full -->
```python
from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models

from apps.account.models import AccountOwnedModel


class Job(AccountOwnedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=80)
    idempotency_key = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=Status, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    result = models.JSONField(default=dict)
    error_code = models.CharField(max_length=80, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    objects: models.Manager[Job] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("account", "idempotency_key"),
                name="job_unique_account_idempotency",
            )
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "status", "-created_at"),
                name="job_account_status_idx",
            )
        ]
```

<!-- artifact: src/apps/jobs/serializers.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework import serializers

from apps.jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "kind",
            "status",
            "attempts",
            "result",
            "error_code",
            "created_at",
            "started_at",
            "finished_at",
        )
        read_only_fields = fields
```

<!-- artifact: src/apps/jobs/views.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer


class JobViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(account=self.request.user.account)
```

<!-- artifact: src/apps/jobs/urls.py; profiles: celery-postgres-results,tasks,full -->
```python
from rest_framework.routers import SimpleRouter

from apps.jobs.views import JobViewSet

app_name = "jobs"

router = SimpleRouter()
router.register("", JobViewSet, basename="job")

urlpatterns = router.urls
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: celery-postgres-results -->
```toml
  "django-celery-results==2.6.0",
```

##### Alternatives and trade-offs

Database polling is simple, observable, and reconnect-safe. Push progress
with SSE or WebSockets only when users benefit from lower latency (see
[SSE](#recipesssemd), [Channels](#recipeschannelsmd)).

##### Required tests

Test the model's account/idempotency-key uniqueness constraint, serializer
field set, and that retrieval is scoped to the requesting account.

##### Related standards

See [celery-django](#recipescelerycelery-djangomd) (writes and transitions this model),
[celery-beat](#recipescelerycelery-beatmd), and [the Celery module family](#recipesceleryreadmemd).

### recipes/celery/celery-redis-broker.md

#### Celery Redis Broker

##### Purpose and when to use it

Use this module to document the Redis broker/result-backend configuration
that `celery-core` and every module requiring it depend on. Requires only
`celery-core`.

##### When not to use it

This module has no independent effect — it exists so "which modules need
Redis" is answerable without reading `celery-core`'s own doc. Requesting it
without `celery-core` is meaningless (and `celery-core` is pulled in
automatically since this module requires it).

##### Responsibilities and invariants

This module owns no artifact of its own. The broker URL, result backend,
and Redis connection settings are aggregator-owned, exactly like every
other project-wide setting: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`,
and `REDIS_URL` live unconditionally in
[`src/core/settings/celery.py`](#srccoresettingscelerymd) and
[`src/core/settings/channels.py`](#srccoresettingschannelsmd)
(`base` artifacts) and
[`.env.example`](#environmentmd) (also `base`), because a setting
module cannot vary per selected module the way feature code can — see
["project aggregators... remain owned by their top-level standards"](#recipesreadmemd).
The `celery[redis]` dependency itself is pinned by `celery-core`'s own
dependency-fragment in [`src/core/celery.md`](#srccorecelerymd),
since this template never uses Celery with a different broker.

##### Alternatives and trade-offs

Bundling the `[redis]` extra into `celery-core` rather than giving this
module its own dependency-fragment avoids a package listed twice with
different extras; the cost is that a hypothetical non-Redis broker would
require editing `celery-core` directly rather than swapping this module out.

##### Required tests

Covered by [celery-django](#recipescelerycelery-djangomd)'s worker-against-Redis
integration test; this module has no independent test surface.

##### Related standards

See [the Celery application](#srccorecelerymd),
[environment](#environmentmd), and
[the Celery module family](#recipesceleryreadmemd).

### recipes/channels.md

#### Channels and Daphne WebSockets

##### Purpose and when to use it

Use Channels when clients need bidirectional, long-lived communication or
server-pushed account events over WebSockets. Daphne serves the ASGI
application, Redis carries group messages between processes, and PostgreSQL
provides reconnect replay.

##### When not to use it

Use REST for request-response operations and SSE for one-way browser streams.
Do not put authorization only in the connection URL, trust `Origin`, or assume
Redis group delivery is durable.

##### Responsibilities and invariants

- `ProtocolTypeRouter` keeps ordinary Django HTTP and WebSockets explicit.
- `AllowedHostsOriginValidator` rejects untrusted browser origins.
- Authentication is resolved before the consumer accepts the socket.
- Every subscription verifies account ownership.
- Group names are derived from validated server-side identifiers.
- Persisted event IDs support reconnect; Redis only reduces delivery latency.
- Clients reconnect with bounded exponential backoff and their last event ID.

##### Complete canonical artifacts

The middleware accepts the same short-lived JWT used by the REST API in the
`Authorization: Bearer` handshake header. Browsers that cannot set handshake
headers should exchange their authenticated session for a short-lived,
single-purpose socket ticket over HTTPS rather than placing a long-lived token
in the query string.

<!-- artifact: src/apps/realtime/auth.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.authentication.models import User

ASGIApp = Callable[
    [
        dict[str, Any],
        Callable[[], Awaitable[dict[str, Any]]],
        Callable[[dict[str, Any]], Awaitable[None]],
    ],
    Awaitable[None],
]


def _bearer_token(headers: list[tuple[bytes, bytes]]) -> str | None:
    authorization = next(
        (value for name, value in headers if name.lower() == b"authorization"),
        b"",
    )
    scheme, separator, token = authorization.partition(b" ")
    if separator == b"" or scheme.lower() != b"bearer":
        return None
    try:
        return token.decode("ascii")
    except UnicodeDecodeError:
        return None


async def _authenticate(headers: list[tuple[bytes, bytes]]) -> User | AnonymousUser:
    encoded = _bearer_token(headers)
    if encoded is None:
        return AnonymousUser()
    try:
        token = AccessToken(
            encoded  # ty: ignore[invalid-argument-type]  # SimpleJWT accepts encoded text at runtime.
        )
        user_id = token["user_id"]
        return await User.objects.aget(pk=user_id, is_active=True)
    except KeyError, ObjectDoesNotExist, TokenError:
        return AnonymousUser()


class JwtAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        authenticated_scope = dict(scope)
        authenticated_scope["user"] = await _authenticate(scope.get("headers", []))
        await self.app(authenticated_scope, receive, send)
```

<!-- artifact: src/apps/realtime/consumers.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.account.models import Account
from apps.realtime.models import StreamEvent


class AccountEventConsumer(AsyncJsonWebsocketConsumer):
    group_name: str
    account_id: str

    async def connect(self) -> None:
        user = self.scope["user"]
        self.account_id = str(self.scope["url_route"]["kwargs"]["account_id"])
        account_is_allowed = (
            user.is_authenticated
            and await Account.objects.filter(
                pk=self.account_id,
                user=user,
                is_active=True,
            ).aexists()
        )
        if not account_is_allowed:
            await self.close(code=4403)
            return

        self.group_name = f"account.{self.account_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        raw_after = parse_qs(self.scope.get("query_string", b"").decode("ascii")).get(
            "after", ["0"]
        )[0]
        try:
            after_id = max(0, int(raw_after))
        except ValueError:
            await self.close(code=4400)
            return

        events = StreamEvent.objects.filter(
            account_id=self.account_id,
            id__gt=after_id,
        ).order_by("id")
        async for event in events.aiterator(chunk_size=100):
            await self.send_json(
                {
                    "id": event.pk,
                    "topic": event.topic,
                    "type": event.event_type,
                    "payload": event.payload,
                }
            )

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def account_event(self, event: dict[str, object]) -> None:
        await self.send_json(event["message"])
```

<!-- artifact: src/apps/realtime/publish.py; profiles: realtime-channels,realtime,full -->
```python
from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from apps.account.models import Account
from apps.realtime.models import StreamEvent


@transaction.atomic
def publish_account_event(
    *,
    account: Account,
    topic: str,
    event_type: str,
    payload: dict[str, object],
) -> StreamEvent:
    event = StreamEvent.objects.create(
        account=account,
        topic=topic,
        event_type=event_type,
        payload=payload,
    )

    def notify() -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            f"account.{account.pk}",
            {
                "type": "account.event",
                "message": {
                    "id": event.pk,
                    "topic": event.topic,
                    "type": event.event_type,
                    "payload": event.payload,
                },
            },
        )

    transaction.on_commit(notify)
    return event
```

<!-- artifact: src/apps/realtime/routing.py; profiles: realtime-channels,realtime,full -->
```python
from django.urls import path

from apps.realtime.consumers import AccountEventConsumer

websocket_urlpatterns = [
    path(
        "ws/accounts/<int:account_id>/events/",
        AccountEventConsumer.as_asgi(),
    )
]
```

This complete application artifact can be used directly with
`daphne apps.realtime.application:application`. The central core ASGI standard
may expose the same composition when `realtime` is selected.

<!-- artifact: src/apps/realtime/application.py; profiles: realtime-channels,realtime,full -->
```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.realtime.auth import JwtAuthMiddleware
from apps.realtime.routing import websocket_urlpatterns

django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                JwtAuthMiddleware(
                    URLRouter(websocket_urlpatterns),
                )
            )
        ),
    }
)
```

<!-- artifact: src/apps/realtime/tests/test_websocket.py; profiles: realtime-channels,realtime,full -->
```python
import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from rest_framework_simplejwt.tokens import AccessToken

from apps.account.models import Account
from apps.authentication.models import User
from apps.realtime.application import application


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_authenticated_socket_receives_group_event() -> None:
    # Arrange
    user = await User.objects.acreate(email="socket@example.test")
    account = await Account.objects.acreate(user=user)
    token = AccessToken.for_user(user)
    communicator = WebsocketCommunicator(
        application,
        f"/ws/accounts/{account.pk}/events/?after=0",
        headers=[
            (b"host", b"localhost"),
            (b"origin", b"http://localhost"),
            (b"authorization", f"Bearer {token}".encode()),
        ],
    )
    channel_layer = get_channel_layer()
    if channel_layer is None:
        raise RuntimeError("Channel layer is not configured.")

    # Act
    connected, _subprotocol = await communicator.connect()
    await channel_layer.group_send(
        f"account.{account.pk}",
        {
            "type": "account.event",
            "message": {
                "id": 1,
                "topic": "jobs",
                "type": "progress",
                "payload": {"percent": 50},
            },
        },
    )
    message = await communicator.receive_json_from()
    await communicator.disconnect()

    # Assert
    assert connected is True
    assert message == {
        "id": 1,
        "topic": "jobs",
        "type": "progress",
        "payload": {"percent": 50},
    }


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_untrusted_origin_is_rejected() -> None:
    # Arrange
    communicator = WebsocketCommunicator(
        application,
        "/ws/accounts/1/events/",
        headers=[
            (b"host", b"testserver"),
            (b"origin", b"https://untrusted.example.test"),
        ],
    )

    # Act
    connected, _subprotocol = await communicator.connect()

    # Assert
    assert connected is False
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: realtime-channels -->
```toml
  "channels==4.3.2",
  "channels-redis==4.3.0",
  "daphne==4.2.3",
```

<!-- dependency-fragment: pyproject.toml#dev; modules: realtime-channels -->
```toml
  "pytest-asyncio==1.4.0",
  "websockets==15.0.1",
```

<!-- dependency-fragment: pyproject.toml#pytest; modules: realtime-channels -->
```toml
asyncio_mode = "auto"
```

##### Alternatives and trade-offs

Running all HTTP under Daphne simplifies one deployment and supports SSE and
WebSockets. Splitting WSGI REST and ASGI realtime services can isolate scaling
and failure modes but requires shared authentication, deployment, and routing
configuration. Redis groups are ephemeral; the event table provides recovery.

##### Required tests

Test missing, expired, and malformed tokens; foreign accounts; inactive users;
untrusted and absent origins; replay after reconnect; Redis group delivery;
disconnect cleanup; backpressure; and worker restart. Use
`WebsocketCommunicator` for protocol behavior and smoke-test Daphne with Redis
in the integration environment.

##### Related standards

- [SSE](#recipesssemd)
- [Deployment](#recipesdeploymentmd)
- [Security](#docssecuritymd)
- [Operations](#docsoperationsmd)

### recipes/chat.md

#### Chat Streaming over Celery, Redis Streams, and SSE

##### Purpose and when to use it

Use this transport when a browser needs to watch a multi-turn assistant
conversation stream token-by-token without holding a synchronous worker for
the duration of the agent turn. The HTTP request that starts a turn returns
immediately after enqueuing a Celery task; the task runs the agent and relays
every event onto a per-thread Redis Stream; an async SSE view tails that
stream and forwards events to the browser as they arrive. The SSE view never
reads the Celery result backend — it only ever reads Redis — so a terminal
event MUST be published on every code path, including failures, or a client
would hang until its own timeout.

This recipe assumes [OpenAI and Deep Agents](#recipesopenai-deep-agentsmd) supplies
`ChatService`, `ChatStreamEvent`, and `get_thread_id`. It is deliberately
narrower than [ordered SSE](#recipesssemd): chat events are ephemeral relay traffic
scoped to one in-flight turn, not a durable, replayable, account-scoped event
log, so a Redis Stream with a short TTL is enough and a PostgreSQL-backed
model would be unused overhead.

##### When not to use it

Use a direct synchronous call to `ChatService.chat` when the product can wait
for one HTTP response and does not need incremental tokens. Use
[ordered SSE](#recipesssemd) instead when clients must reconnect after minutes or
hours and replay history from a durable cursor — Redis Streams here expire
with the turn and are not a long-term record. Use [Channels](#recipeschannelsmd)
instead when the browser must also send low-latency messages on the same
connection, such as interrupting a running agent turn.

##### Responsibilities and invariants

- `ChatStartAPIView` only enqueues a task; it never runs the agent inline.
- The Celery task publishes every `ChatStreamEvent` the agent produces, in
  order, to `chat:stream:<thread_id>`.
- The task publishes a terminal `error` event on every failure path —
  guardrail rejection and unexpected exceptions alike — so the SSE view
  always reaches a stopping point instead of blocking until its own timeout.
- The stream key gets a TTL in a `finally` block so abandoned or completed
  streams are reclaimed regardless of outcome.
- The SSE view runs under ASGI, reads with a blocking `XREAD` cursor, and
  stops as soon as it forwards a `complete` or `error` event.
- The SSE view enforces its own wall-clock timeout independent of the
  gunicorn/ASGI worker timeout, and the deployed worker timeout stays
  comfortably above it so the platform never kills the connection first.
- A periodic heartbeat is unnecessary here because `XREAD` with `block`
  already bounds how long the view can be idle before re-checking its own
  deadline; do not add polling sleeps on top of the blocking read.
- History and message content are never logged.

##### Complete canonical artifacts

<!-- artifact: src/apps/chat/apps.py; profiles: chat-streaming,vector-ai,full -->
```python
from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
```

<!-- artifact: src/apps/chat/redis.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import redis
import redis.asyncio as aredis
from django.conf import settings

if TYPE_CHECKING:
    from apps.assistants.types import ChatStreamEvent

_sync_client: redis.Redis | None = None


def stream_key(thread_id: str) -> str:
    """Return the Redis Stream key that relays chat events for one thread."""
    return f"chat:stream:{thread_id}"


def get_sync_redis_client() -> redis.Redis:
    """Return a process-wide sync Redis client, used by the Celery worker."""
    global _sync_client
    if _sync_client is None:
        _sync_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _sync_client


def get_async_redis_client() -> aredis.Redis:
    """Return a new async Redis client bound to the caller's event loop, used by the SSE view."""
    return aredis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_event(client: redis.Redis, *, thread_id: str, event: ChatStreamEvent) -> str:
    """Append one chat stream event to the thread's Redis Stream."""
    return client.xadd(stream_key(thread_id), {"event": json.dumps(event)})


def expire_stream(client: redis.Redis, *, thread_id: str, ttl_seconds: int) -> None:
    """Set a TTL on the thread's stream so finished or abandoned streams get cleaned up."""
    client.expire(stream_key(thread_id), ttl_seconds)


def decode_entry(fields: dict[str, str]) -> ChatStreamEvent:
    """Decode a raw Redis Stream entry's fields back into a ChatStreamEvent."""
    return json.loads(fields["event"])
```

<!-- artifact: src/apps/chat/tasks.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings

from apps.assistants.chat import ChatService
from apps.assistants.types import ChatMessage
from apps.chat.redis import expire_stream, get_sync_redis_client, publish_event

logger = logging.getLogger(__name__)


@shared_task
def run_chat_stream_task(*, thread_id: str, message: str, history: list[ChatMessage] | None = None) -> None:
    """Run one chat turn and relay every streamed event to the thread's Redis Stream.

    The SSE view only ever reads from Redis, never from this task's Celery result, so a
    terminal "error" event MUST be published on every failure path or the SSE client would
    hang until its own timeout instead of failing fast.
    """
    client = get_sync_redis_client()
    try:
        for event in ChatService().stream(message, history):
            publish_event(client, thread_id=thread_id, event=event)

    except (ValueError, RuntimeError) as exc:
        logger.warning("Chat guardrail rejected thread %s: %s", thread_id, exc)
        publish_event(client, thread_id=thread_id, event={"type": "error", "agent": None, "message": str(exc)})

    except Exception:
        logger.exception("Unhandled error streaming chat for thread %s", thread_id)
        publish_event(
            client,
            thread_id=thread_id,
            event={"type": "error", "agent": None, "message": "Something went wrong while generating the response."},
        )
    finally:
        expire_stream(client, thread_id=thread_id, ttl_seconds=settings.CHAT_STREAM_TTL_SECONDS)
```

`CHAT_STREAM_TTL_SECONDS` is a small setting owned by this recipe when
enabled; set it comfortably above the SSE view's `max_wait_seconds` so a slow
consumer can still read the last events before Redis reclaims the key.

<!-- artifact: src/apps/chat/serializers.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()


class ChatStartSerializerRequest(serializers.Serializer):
    message = serializers.CharField(allow_blank=False)
    thread_id = serializers.CharField(required=False, allow_null=True, default=None)
    history = ChatMessageSerializer(many=True, required=False, default=list)


class ChatStartSerializerResponse(serializers.Serializer):
    thread_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
```

<!-- artifact: src/apps/chat/views.py; profiles: chat-streaming,vector-ai,full -->
```python
from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator

from django.http import HttpRequest, StreamingHttpResponse
from django.views import View
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistants.chat import get_thread_id
from apps.assistants.types import ChatStreamEvent
from apps.chat.redis import decode_entry, get_async_redis_client, stream_key
from apps.chat.serializers import ChatStartSerializerRequest, ChatStartSerializerResponse
from apps.chat.tasks import run_chat_stream_task


class ChatStartAPIView(APIView):
    def post(self, request: Request) -> Response:
        input_serializer = ChatStartSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            thread_id = get_thread_id(data["thread_id"])
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

        run_chat_stream_task.delay(thread_id=thread_id, message=data["message"], history=data["history"])

        output_serializer = ChatStartSerializerResponse({"thread_id": thread_id, "status": "accepted"})
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)


class ChatStreamAPIView(View):
    """Relay a thread's Redis Stream to the browser as Server-Sent Events.

    The deployed worker timeout must stay comfortably above `max_wait_seconds`,
    otherwise the platform kills the worker process mid-stream before this view's own
    timeout logic gets a chance to close the connection gracefully.
    """

    max_wait_seconds = 120
    read_block_ms = 15_000

    async def get(self, _request: HttpRequest, thread_id: str) -> StreamingHttpResponse:
        response = StreamingHttpResponse(
            self._event_source(thread_id),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        response["Connection"] = "keep-alive"
        return response

    async def _event_source(self, thread_id: str) -> AsyncIterator[bytes]:
        client = get_async_redis_client()
        key = stream_key(thread_id)
        last_id = "0"
        deadline = time.monotonic() + self.max_wait_seconds
        try:
            while True:
                if time.monotonic() > deadline:
                    yield self._sse_format({"type": "error", "agent": None, "message": "Stream timed out."})
                    return

                result = await client.xread({key: last_id}, count=50, block=self.read_block_ms)
                if not result:
                    continue

                for _stream_name, entries in result:
                    for entry_id, fields in entries:
                        last_id = entry_id
                        event = decode_entry(fields)
                        yield self._sse_format(event)
                        if event["type"] in ("complete", "error"):
                            return
        finally:
            await client.aclose()

    @staticmethod
    def _sse_format(event: ChatStreamEvent) -> bytes:
        return f"data: {json.dumps(event)}\n\n".encode()
```

`ChatStartAPIView` inherits the project's default authentication and
permission classes; scope the enqueued thread to `request.user` (for example
by prefixing `stream_key` with the account id) whenever chat history is
account-owned rather than anonymous.

<!-- artifact: src/apps/chat/urls.py; profiles: chat-streaming,vector-ai,full -->
```python
from django.urls import path

from apps.chat.views import ChatStartAPIView, ChatStreamAPIView

app_name = "chat"

urlpatterns = [
    path("chat", ChatStartAPIView.as_view(), name="chat-start"),
    path("chat/<str:thread_id>/events", ChatStreamAPIView.as_view(), name="chat-stream"),
]
```

<!-- artifact: src/apps/chat/tests/test_chat_start_api.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@patch("apps.chat.views.run_chat_stream_task")
def test_start_enqueues_a_task_and_returns_a_thread_id(
    task: object,
    api_client: APIClient,
) -> None:
    # Act
    response = api_client.post(
        reverse("chat:chat-start"),
        {"message": "Hi there"},
        format="json",
    )

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["status"] == "accepted"
    assert response.data["thread_id"]
    task.delay.assert_called_once_with(
        thread_id=response.data["thread_id"],
        message="Hi there",
        history=[],
    )


def test_start_rejects_a_blank_message(api_client: APIClient) -> None:
    # Act
    response = api_client.post(reverse("chat:chat-start"), {"message": ""}, format="json")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("apps.chat.views.run_chat_stream_task")
def test_start_rejects_a_blank_thread_id(task: object, api_client: APIClient) -> None:
    # Act
    response = api_client.post(
        reverse("chat:chat-start"),
        {"message": "Hi", "thread_id": "   "},
        format="json",
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    task.delay.assert_not_called()
```

<!-- artifact: src/apps/chat/tests/test_chat_stream_view.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import AsyncMock

import pytest
from django.urls import reverse

from apps.chat.views import ChatStreamAPIView


@pytest.mark.asyncio
async def test_event_source_forwards_events_and_stops_at_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    client = AsyncMock()
    client.xread.side_effect = [
        [("chat:stream:t1", [("1-0", {"event": '{"type": "token", "agent": "assistant", "content": "Hi"}'})])],
        [("chat:stream:t1", [("2-0", {"event": '{"type": "complete", "history": []}'})])],
    ]
    monkeypatch.setattr("apps.chat.views.get_async_redis_client", lambda: client)
    view = ChatStreamAPIView()

    # Act
    chunks = [chunk async for chunk in view._event_source("t1")]

    # Assert
    assert b'"type": "token"' in chunks[0] or b'"type":"token"' in chunks[0].replace(b" ", b"")
    assert b"complete" in chunks[-1]
    client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_source_times_out_when_nothing_is_published(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    client = AsyncMock()
    client.xread.return_value = []
    monkeypatch.setattr("apps.chat.views.get_async_redis_client", lambda: client)
    clock = iter([0.0, 0.0, 200.0])
    monkeypatch.setattr("apps.chat.views.time.monotonic", lambda: next(clock))
    view = ChatStreamAPIView()
    view.max_wait_seconds = 1

    # Act
    chunks = [chunk async for chunk in view._event_source("t1")]

    # Assert
    assert b"timed out" in chunks[-1]
    client.aclose.assert_awaited_once()


def test_stream_url_routes_to_the_thread(client: object) -> None:
    # Assert
    assert reverse("chat:chat-stream", kwargs={"thread_id": "abc"}) == "/chat/abc/events"
```

<!-- artifact: src/apps/chat/tests/test_redis_helpers.py; profiles: chat-streaming,vector-ai,full -->
```python
from unittest.mock import Mock

from apps.chat.redis import decode_entry, expire_stream, publish_event, stream_key


def test_stream_key_is_namespaced_per_thread() -> None:
    # Assert
    assert stream_key("abc-123") == "chat:stream:abc-123"


def test_publish_event_serializes_json_onto_the_stream() -> None:
    # Arrange
    client = Mock()
    event = {"type": "token", "agent": "assistant", "content": "Hi"}

    # Act
    publish_event(client, thread_id="t1", event=event)

    # Assert
    client.xadd.assert_called_once()
    args, kwargs = client.xadd.call_args
    assert args[0] == "chat:stream:t1"
    assert decode_entry(args[1]) == event


def test_expire_stream_sets_the_configured_ttl() -> None:
    # Arrange
    client = Mock()

    # Act
    expire_stream(client, thread_id="t1", ttl_seconds=300)

    # Assert
    client.expire.assert_called_once_with("chat:stream:t1", 300)
```

<!-- dependency-fragment: pyproject.toml#dev; modules: chat-streaming -->
```toml
  "pytest-asyncio==1.4.0",
```

<!-- dependency-fragment: pyproject.toml#pytest; modules: chat-streaming -->
```toml
asyncio_mode = "auto"
```

##### Alternatives and trade-offs

Streaming the agent's response directly from a synchronous ASGI view avoids
Celery and Redis entirely, but ties the response to one HTTP connection: a
client refresh loses the in-flight turn, and a single slow agent call occupies
an ASGI worker for its full duration. Relaying through a Celery task and a
Redis Stream decouples turn execution from the viewer's connection — the
worker can retry or run independently of the browser, and any number of tabs
could tail the same `thread_id`. The trade-off is two extra hops and a second
place (Redis) where "what happened during this turn" briefly lives; the TTL
keeps that window short and cheap rather than promoting it to a durable
record. Reach for [ordered SSE](#recipesssemd)'s PostgreSQL-backed model instead when
a durable, replayable transcript is itself a product requirement.

##### Required tests

Cover the start endpoint's enqueue and validation paths, the SSE view's event
forwarding, timeout, and cleanup, and the Redis helpers' key namespacing and
serialization. Run one integration test with a real Celery worker (eager mode
disabled) and a real Redis instance driving the full task through the SSE
view, confirming a terminal event is always published, including when the
agent raises.

##### Related standards

- [OpenAI and Deep Agents](#recipesopenai-deep-agentsmd)
- [Celery module family](#recipesceleryreadmemd)
- [SSE](#recipesssemd)
- [Channels](#recipeschannelsmd)
- [Testing](#docstestingmd)

### recipes/deployment.md

#### WSGI and ASGI Deployment

##### Purpose and when to use it

Choose the server from the connection behavior, not from habit. Gunicorn with
WSGI workers is a strong default for synchronous REST APIs. Daphne with ASGI is
required for the long-lived SSE and WebSocket examples. An integrated project
may send all traffic to Daphne or split REST and realtime traffic into
separately scaled services.

| Concern | Gunicorn and WSGI | Daphne and ASGI |
| --- | --- | --- |
| Synchronous REST | Recommended default | Supported |
| Long-lived SSE | Occupies a worker | Recommended |
| WebSockets | Not supported by WSGI | Supported |
| Scaling unit | Request workers | Connections and event-loop capacity |
| Failure isolation | Simple REST-only process | Can be split from REST |
| Application target | `core.wsgi:application` | `apps.realtime.application:application` |

##### When not to use it

Do not place SSE or WebSockets behind synchronous workers, expose development
servers in production, or add a second serving stack without monitoring and
capacity tests. Kubernetes, another process supervisor, or a managed platform
can replace the systemd examples while preserving the same process contracts.

##### Responsibilities and invariants

- TLS terminates at a trusted load balancer or reverse proxy.
- Proxy timeouts exceed expected stream duration and buffering is off for SSE.
- WebSocket upgrade headers are forwarded only to the ASGI service.
- Readiness checks verify dependencies; liveness checks only verify the process.
- Workers receive graceful shutdown and enough time to finish or cancel work.
- Secrets live in the runtime environment file, never in service definitions.
- Static assets are served by object storage or a proxy, not Django workers.
- Deployments run migrations as one explicit release step before new workers.

##### Complete canonical artifacts

The synchronous profiles and the integrated profile can run REST through
Gunicorn. The service is intentionally independent of a particular cloud.

<!-- artifact: deploy/systemd/generic-api-rest.ini; profiles: base,tasks,storage,vector-ai,full -->
```ini
[Unit]
Description=Generic Django REST API
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=django
Group=django
WorkingDirectory=/srv/generic-api/src
EnvironmentFile=/etc/generic-api/environment
ExecStart=/srv/generic-api/.venv/bin/gunicorn --config /srv/generic-api/gunicorn.conf.py core.wsgi:application --bind 127.0.0.1:8000 --workers 3 --worker-tmp-dir /dev/shm --access-logfile - --error-logfile -
ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGTERM
TimeoutStopSec=45
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

The realtime profiles run Daphne. Capacity-test the process count and maximum
connections with production-like message rates.

<!-- artifact: deploy/systemd/generic-api-realtime.ini; profiles: realtime-sse,realtime-channels,realtime,full -->
```ini
[Unit]
Description=Generic Django Realtime API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=django
Group=django
WorkingDirectory=/srv/generic-api/src
EnvironmentFile=/etc/generic-api/environment
ExecStart=/srv/generic-api/.venv/bin/daphne --bind 127.0.0.1 --port 8001 --proxy-headers core.asgi:application
KillSignal=SIGTERM
TimeoutStopSec=45
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

This proxy configuration sends REST to Gunicorn and only long-lived endpoints
to Daphne. The upstream proxy is also responsible for HTTPS and security
headers in the production environment.

<!-- artifact: deploy/nginx/realtime.conf; profiles: realtime-sse,realtime-channels,realtime,full -->
```text
upstream django_rest {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream django_realtime {
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 443 ssl;
    server_name api.example.test;

    ssl_certificate /etc/generic-api/tls/certificate.pem;
    ssl_certificate_key /etc/generic-api/tls/private-key.pem;

    client_max_body_size 2m;

    location /api/v1/events/ {
        proxy_pass http://django_realtime;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 1h;
        add_header X-Accel-Buffering no;
    }

    location /ws/ {
        proxy_pass http://django_realtime;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 1h;
    }

    location / {
        proxy_pass http://django_rest;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
    }
}
```

##### Alternatives and trade-offs

One Daphne service reduces routing complexity and can serve REST, SSE, and
WebSockets together. A split deployment protects ordinary API latency from
large connection counts and permits different scaling, but doubles serving
configuration and health monitoring. Gunicorn can also host an ASGI worker,
but its lifecycle and feature support must be verified against the pinned
versions rather than assumed.

##### Required tests

Validate service and proxy syntax, forwarded host and scheme handling, trusted
proxy configuration, graceful termination, migration ordering, readiness and
liveness behavior, static-file routing, body limits, SSE buffering and
heartbeat visibility, WebSocket upgrade and origin rejection, reconnect during
a rolling deployment, and capacity at expected concurrent connection counts.

##### Related standards

- [Operations](#docsoperationsmd)
- [Security](#docssecuritymd)
- [SSE](#recipesssemd)
- [Channels](#recipeschannelsmd)

### recipes/openai-deep-agents.md

#### Optional OpenAI and Deep Agents Integration

##### Purpose and when to use it

Use this optional adapter when a generic assistant needs OpenAI text generation,
embeddings, or a genuinely multi-step agent. The domain calls a small provider
boundary; it does not import the OpenAI SDK or Deep Agents. Simple generation
and embedding use the Responses and Embeddings APIs directly. Multi-step work
uses Deep Agents for planning, tool use, context management, and subagents.
The example uses
`gpt-5.6-sol`, `store=False`, a stable privacy-preserving
`safety_identifier`, streamed typed events, and
`text-embedding-3-small`.

The request shape follows the current
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6),
[streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses),
[safety guidance](https://developers.openai.com/api/docs/guides/safety-best-practices),
and [embeddings guide](https://developers.openai.com/api/docs/guides/embeddings).

##### When not to use it

Do not add a model provider to deterministic CRUD, hide authorization inside a
prompt, or use an agent for one model call with no tools or delegation. Do not
send private content until retention, region, access, evaluation, and incident
requirements are decided.

##### Responsibilities and invariants

- Vendor code remains behind a domain-neutral protocol.
- The API key comes only from the runtime environment.
- `store=False` is explicit on every Responses request in this example.
- A dedicated secret derives a stable opaque safety identifier; raw user data
  is not sent as the identifier.
- Streaming distinguishes text, refusal, completion, rate limits, and provider
  failures.
- HTTP layers translate provider exceptions to the standard error envelope.
- Tests replace the client completely and never call a live API.
- Embedding model and 1536-dimension schema change together.
- Deep Agents owns multi-step orchestration; application code does not build
  LangChain chains or LangGraph graphs directly.
- Agent tools enforce account ownership and authorization in Python before each
  read or mutation; prompts are never a security boundary.
- Persistence is opt-in and must use a production checkpointer and store chosen
  for the application's retention and tenant-isolation requirements.

##### Complete canonical artifacts

<!-- artifact: src/apps/assistants/contracts.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True, slots=True)
class AssistantChunk:
    kind: Literal["text", "refusal", "completed"]
    text: str = ""


class AssistantProvider(Protocol):
    def stream_answer(
        self,
        *,
        user_id: object,
        prompt: str,
    ) -> Iterator[AssistantChunk]:
        pass


class EmbeddingProvider(Protocol):
    model_name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        pass
```

<!-- artifact: src/apps/assistants/openai_provider.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

import hashlib
import hmac
from collections.abc import Iterator, Sequence
from typing import Any

from django.conf import settings
from openai import OpenAI, OpenAIError, RateLimitError

from apps.assistants.contracts import AssistantChunk

TEXT_MODEL = "gpt-5.6-sol"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


class AssistantRateLimited(Exception):
    pass


class AssistantProviderUnavailable(Exception):
    pass


def safety_identifier(user_id: object) -> str:
    secret = settings.OPENAI_SAFETY_IDENTIFIER_SECRET.encode()
    digest = hmac.new(
        secret,
        str(user_id).encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"user_{digest}"


class OpenAIProvider:
    model_name = EMBEDDING_MODEL

    def __init__(self, client: Any | None = None) -> None:
        self.client = client or OpenAI(api_key=settings.OPENAI_API_KEY)

    def stream_answer(
        self,
        *,
        user_id: object,
        prompt: str,
    ) -> Iterator[AssistantChunk]:
        if not prompt.strip():
            raise ValueError("prompt must contain text")
        try:
            stream = self.client.responses.create(
                model=TEXT_MODEL,
                instructions=(
                    "Answer the user's question accurately and concisely. "
                    "State uncertainty instead of inventing facts."
                ),
                input=prompt,
                reasoning={"effort": "none"},
                safety_identifier=safety_identifier(user_id),
                store=False,
                stream=True,
            )
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield AssistantChunk(kind="text", text=event.delta)
                elif event.type == "response.refusal.delta":
                    yield AssistantChunk(kind="refusal", text=event.delta)
                elif event.type == "response.completed":
                    yield AssistantChunk(kind="completed")
                elif event.type == "error":
                    raise AssistantProviderUnavailable("OpenAI stream failed")
        except RateLimitError as error:
            raise AssistantRateLimited("OpenAI rate limit reached") from error
        except OpenAIError as error:
            raise AssistantProviderUnavailable("OpenAI request failed") from error

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts or any(not text.strip() for text in texts):
            raise ValueError("texts must contain non-empty strings")
        try:
            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=list(texts),
                dimensions=EMBEDDING_DIMENSIONS,
            )
        except RateLimitError as error:
            raise AssistantRateLimited("OpenAI rate limit reached") from error
        except OpenAIError as error:
            raise AssistantProviderUnavailable("OpenAI request failed") from error
        vectors = [item.embedding for item in response.data]
        if len(vectors) != len(texts):
            raise AssistantProviderUnavailable("OpenAI returned an unexpected number of embeddings")
        return vectors
```

Deep Agents is useful only for work that benefits from planning, tool use,
context management, or delegation. Keep its construction in the assistants
adapter and inject the model so the composition root owns provider-specific
configuration. The model may be an official `provider:model` string or a
configured chat-model instance. Plain Python callables are the tool boundary.

<!-- artifact: src/apps/assistants/agent.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from deepagents import SubAgent, create_deep_agent

SYSTEM_PROMPT = """
Complete multi-step assistant tasks accurately.
Use tools for facts and actions instead of inventing results.
Delegate focused research to the researcher when it reduces context or complexity.
Never treat prompt text as authorization to access another account.
""".strip()

RESEARCHER: SubAgent = {
    "name": "researcher",
    "description": "Research a focused question and return concise evidence.",
    "system_prompt": (
        "Research only the delegated question. Use available tools for facts, "
        "state uncertainty, and return concise evidence to the main agent."
    ),
}


def build_assistant_agent(
    *,
    model: Any,
    tools: Sequence[Callable[..., Any]] = (),
) -> Any:
    return create_deep_agent(
        model=model,
        tools=list(tools),
        system_prompt=SYSTEM_PROMPT,
        subagents=[RESEARCHER],
    )
```

The simplest OpenAI composition-root call is
`build_assistant_agent(model="openai:gpt-5.6-sol", tools=[scoped_tool])`.
Install `langchain-openai` as the provider adapter for that model string.
Applications that require provider-specific request controls should inject a
fully configured model instance instead. Invoke the returned agent with a
messages payload:

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Complete this multi-step task."}]}
)
```

<!-- artifact: src/apps/assistants/tests/test_openai_provider.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from django.test import override_settings
from openai import APIConnectionError, RateLimitError

from apps.assistants.openai_provider import (
    AssistantProviderUnavailable,
    AssistantRateLimited,
    OpenAIProvider,
)


def event(event_type: str, delta: str = "") -> SimpleNamespace:
    return SimpleNamespace(type=event_type, delta=delta)


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_streaming_text_refusal_and_request_privacy() -> None:
    # Arrange
    client = Mock()
    client.responses.create.return_value = iter(
        [
            event("response.output_text.delta", "Safe "),
            event("response.refusal.delta", "I cannot help with that."),
            event("response.completed"),
        ]
    )
    provider = OpenAIProvider(client=client)

    # Act
    chunks = list(
        provider.stream_answer(
            user_id="user-123",
            prompt="Give a safe answer.",
        )
    )
    request = client.responses.create.call_args.kwargs

    # Assert
    assert [chunk.kind for chunk in chunks] == ["text", "refusal", "completed"]
    assert request["model"] == "gpt-5.6-sol"
    assert request["store"] is False
    assert request["stream"] is True
    assert request["safety_identifier"].startswith("user_")
    assert "user-123" not in request["safety_identifier"]


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_rate_limit_is_a_domain_exception() -> None:
    # Arrange
    client = Mock()
    response = httpx.Response(
        429,
        request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
    )
    client.responses.create.side_effect = RateLimitError(
        "rate limited",
        response=response,
        body={"error": {"message": "rate limited"}},
    )
    provider = OpenAIProvider(client=client)

    # Assert
    with pytest.raises(AssistantRateLimited):
        list(provider.stream_answer(user_id="user-123", prompt="Hello"))


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_provider_failure_is_a_domain_exception() -> None:
    # Arrange
    client = Mock()
    client.responses.create.side_effect = APIConnectionError(
        request=httpx.Request("POST", "https://api.openai.com/v1/responses")
    )
    provider = OpenAIProvider(client=client)

    # Assert
    with pytest.raises(AssistantProviderUnavailable):
        list(provider.stream_answer(user_id="user-123", prompt="Hello"))


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_embeddings_are_deterministic_without_a_live_api() -> None:
    # Arrange
    client = Mock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(embedding=[0.0] * 1536),
            SimpleNamespace(embedding=[1.0] * 1536),
        ]
    )
    provider = OpenAIProvider(client=client)

    # Act
    vectors = provider.embed(["first", "second"])

    # Assert
    assert len(vectors) == 2
    assert all(len(vector) == 1536 for vector in vectors)
    client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input=["first", "second"],
        dimensions=1536,
    )
```

##### Multi-turn chat orchestration

A conversational product needs a stable transport contract on top of the agent:
caller-supplied history in, a normalized event stream or updated history out.
Keep this orchestration in the domain app, independent of how the events reach
the browser. [Chat streaming](#recipeschatmd) covers the Celery-and-SSE transport that
consumes the stream produced here.

<!-- artifact: src/apps/assistants/types.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatTokenEvent(TypedDict):
    type: Literal["token"]
    agent: str
    content: str


class ChatAgentEvent(TypedDict):
    type: Literal["agent"]
    agent: str
    status: Literal["started", "completed", "failed", "interrupted"]


class ChatCompleteEvent(TypedDict):
    type: Literal["complete"]
    history: list[ChatMessage]


class ChatErrorEvent(TypedDict):
    type: Literal["error"]
    agent: str | None
    message: str


ChatStreamEvent = ChatTokenEvent | ChatAgentEvent | ChatCompleteEvent | ChatErrorEvent
```

<!-- artifact: src/apps/assistants/guardrails.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from dataclasses import dataclass

from apps.assistants.types import ChatMessage


@dataclass(frozen=True)
class ChatGuardrails:
    """Fast boundary validation applied before and after every chat run."""

    max_message_chars: int = 4_000
    max_history_messages: int = 100

    def validate_input(self, message: str, history: list[ChatMessage]) -> None:
        self._validate_content(message, label="Message")
        if len(history) > self.max_history_messages:
            raise ValueError(f"History cannot contain more than {self.max_history_messages} messages.")
        for index, row in enumerate(history):
            if not isinstance(row, dict) or row.get("role") not in {"user", "assistant"}:
                raise ValueError(f"History message {index} has an invalid role.")
            self._validate_content(row.get("content"), label=f"History message {index}")

    def validate_output(self, history: list[ChatMessage]) -> None:
        if not history or history[-1]["role"] != "assistant" or not history[-1]["content"].strip():
            raise RuntimeError("The chat agent did not return a final assistant message.")

    def _validate_content(self, content: object, *, label: str) -> None:
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"{label} cannot be blank.")
        if len(content) > self.max_message_chars:
            raise ValueError(f"{label} cannot exceed {self.max_message_chars} characters.")
```

Guardrail validation is deliberately plain Python at the boundary, not a model
call: it must reject malformed input before the agent runs and catch a
malformed agent response before it reaches the caller, in both the synchronous
and streaming paths.

<!-- artifact: src/apps/assistants/chat.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol
from uuid import uuid4

from apps.assistants.agent import build_assistant_agent
from apps.assistants.guardrails import ChatGuardrails
from apps.assistants.types import ChatAgentEvent, ChatMessage, ChatStreamEvent


class ChatAgent(Protocol):
    def invoke(self, input: dict[str, object]) -> dict[str, object]: ...

    def stream_events(self, input: dict[str, object], *, version: str): ...


def get_thread_id(thread_id: str | None = None) -> str:
    """Return an existing thread id or create one for a new conversation.

    The caller persists the returned id and reuses it on later turns of the
    same conversation; this function never touches storage itself.
    """
    if thread_id is None:
        return str(uuid4())
    normalized_thread_id = thread_id.strip()
    if not normalized_thread_id:
        raise ValueError("Thread id cannot be blank.")
    return normalized_thread_id


class ChatService:
    """Small Python service around the assistant agent."""

    def __init__(self, *, agent: ChatAgent | None = None, guardrails: ChatGuardrails | None = None) -> None:
        self._agent = agent
        self.guardrails = guardrails or ChatGuardrails()

    @property
    def agent(self) -> ChatAgent:
        if self._agent is None:
            self._agent = build_assistant_agent(model="openai:gpt-5.6-sol")
        return self._agent

    def chat(self, message: str, history: list[ChatMessage] | None = None) -> list[ChatMessage]:
        current_history = list(history or [])
        self.guardrails.validate_input(message, current_history)
        result = self.agent.invoke({"messages": self._input_messages(message=message, history=current_history)})
        updated_history = self._history_from_result(result)
        self.guardrails.validate_output(updated_history)
        return updated_history

    def stream(self, message: str, history: list[ChatMessage] | None = None) -> Iterator[ChatStreamEvent]:
        """Stream agent tokens plus subagent lifecycle events, ending with the final history.

        Delegation to named subagents (see the router-and-specialists pattern
        below) surfaces as interleaved `agent` and `token` events; a single
        flat agent yields only `token` events before `complete`.
        """
        current_history = list(history or [])
        self.guardrails.validate_input(message, current_history)
        stream = self.agent.stream_events(
            {"messages": self._input_messages(message=message, history=current_history)},
            version="v3",
        )

        for event_name, item in stream.interleave("messages", "subagents"):
            if event_name == "messages":
                content = getattr(item, "text", "")
                if content:
                    yield {"type": "token", "agent": "assistant", "content": content}
                continue

            agent_name = getattr(item, "name", "unknown-agent")
            yield {"type": "agent", "agent": agent_name, "status": "started"}
            try:
                for subagent_message in item.messages:
                    content = getattr(subagent_message, "text", "")
                    if content:
                        yield {"type": "token", "agent": agent_name, "content": content}
                _ = item.output
            except Exception:
                yield {"type": "agent", "agent": agent_name, "status": "failed"}
                raise
            yield self._completed_agent_event(agent_name=agent_name, status=getattr(item, "status", "completed"))

        updated_history = self._history_from_result(stream.output)
        self.guardrails.validate_output(updated_history)
        yield {"type": "complete", "history": updated_history}

    @staticmethod
    def _input_messages(*, message: str, history: list[ChatMessage]) -> list[ChatMessage]:
        return [*history, {"role": "user", "content": message}]

    @staticmethod
    def _history_from_result(result: object) -> list[ChatMessage]:
        from langchain_core.messages import BaseMessage

        if not isinstance(result, dict) or not isinstance(result.get("messages"), list):
            raise RuntimeError("The chat agent returned an invalid messages payload.")
        return [
            {"role": "user" if row.type == "human" else "assistant", "content": row.text}
            for row in result["messages"]
            if isinstance(row, BaseMessage) and row.type in {"human", "ai"}
        ]

    @staticmethod
    def _completed_agent_event(*, agent_name: str, status: object) -> ChatAgentEvent:
        normalized_status = status if status in {"completed", "failed", "interrupted"} else "completed"
        return {"type": "agent", "agent": agent_name, "status": normalized_status}
```

A product with more than one specialty benefits from a router that delegates
instead of one agent with every tool. Give each subagent its own
`response_format` so the router receives a small, stable handoff contract
instead of parsing free text:

```python
from typing import Literal

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Small, stable handoff contract from a specialist back to the router."""

    summary: str = Field(description="Concise description of the work performed or information found.")
    record_ids: list[int] = Field(default_factory=list, description="Ids of records created, changed, or selected.")
    next_agent: Literal["billing-agent", "support-agent"] | None = Field(
        default=None,
        description="Specialist that should receive the result next, only when more domain work is required.",
    )
```

Register each specialist as a `SubAgent` with its own system prompt, tools, and
`response_format`, and pass the list to `create_deep_agent(subagents=...)`
instead of a flat `tools` list. Tools stay scoped to the specialist that owns
that part of the domain; the router itself gets no tools and only delegates.

<!-- artifact: src/apps/assistants/tests/test_chat.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from unittest.mock import Mock

import pytest

from apps.assistants.chat import ChatService, get_thread_id
from apps.assistants.guardrails import ChatGuardrails


def _human(text: str) -> Mock:
    return Mock(type="human", text=text)


def _ai(text: str) -> Mock:
    return Mock(type="ai", text=text)


def test_get_thread_id_creates_and_normalizes() -> None:
    # Act / Assert
    assert get_thread_id(None)
    assert get_thread_id("  existing-thread  ") == "existing-thread"
    with pytest.raises(ValueError):
        get_thread_id("   ")


def test_chat_rejects_blank_message_before_invoking_the_agent() -> None:
    # Arrange
    agent = Mock()
    service = ChatService(agent=agent)

    # Assert
    with pytest.raises(ValueError):
        service.chat("   ")
    agent.invoke.assert_not_called()


def test_chat_returns_updated_history_from_the_agent() -> None:
    # Arrange
    agent = Mock()
    agent.invoke.return_value = {"messages": [_human("Hi"), _ai("Hello there.")]}
    service = ChatService(agent=agent)

    # Act
    history = service.chat("Hi")

    # Assert
    assert history == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello there."},
    ]


def test_chat_raises_when_the_agent_returns_no_final_assistant_message() -> None:
    # Arrange
    agent = Mock()
    agent.invoke.return_value = {"messages": [_human("Hi")]}
    service = ChatService(agent=agent)

    # Assert
    with pytest.raises(RuntimeError):
        service.chat("Hi")


def test_stream_yields_tokens_then_the_final_history() -> None:
    # Arrange
    agent = Mock()
    stream = Mock()
    stream.interleave.return_value = iter(
        [("messages", Mock(text="Hel")), ("messages", Mock(text="lo."))]
    )
    stream.output = {"messages": [_human("Hi"), _ai("Hello.")]}
    agent.stream_events.return_value = stream
    service = ChatService(agent=agent)

    # Act
    events = list(service.stream("Hi"))

    # Assert
    assert events[0] == {"type": "token", "agent": "assistant", "content": "Hel"}
    assert events[1] == {"type": "token", "agent": "assistant", "content": "lo."}
    assert events[-1] == {
        "type": "complete",
        "history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello."},
        ],
    }


def test_stream_emits_started_and_completed_events_for_a_delegated_subagent() -> None:
    # Arrange
    agent = Mock()
    stream = Mock()
    subagent_turn = Mock(name="subagent", messages=[_ai("Delegated answer.")], status="completed")
    subagent_turn.name = "billing-agent"
    subagent_turn.output = {}
    stream.interleave.return_value = iter([("subagents", subagent_turn)])
    stream.output = {"messages": [_human("Hi"), _ai("Delegated answer.")]}
    agent.stream_events.return_value = stream
    service = ChatService(agent=agent)

    # Act
    events = list(service.stream("Hi"))

    # Assert
    assert events[0] == {"type": "agent", "agent": "billing-agent", "status": "started"}
    assert events[1] == {"type": "token", "agent": "billing-agent", "content": "Delegated answer."}
    assert events[2] == {"type": "agent", "agent": "billing-agent", "status": "completed"}


def test_guardrails_reject_oversized_history() -> None:
    # Arrange
    guardrails = ChatGuardrails(max_history_messages=1)
    history = [{"role": "user", "content": "one"}, {"role": "assistant", "content": "two"}]

    # Assert
    with pytest.raises(ValueError):
        guardrails.validate_input("three", history)
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: vector-ai-openai -->
```toml
  "httpx==0.28.1",
  "deepagents==0.6.12",
  "langchain-openai==1.4.1",
  "openai==2.48.0",
```

##### Alternatives and trade-offs

A direct Responses call is easier to understand and operate than an agent.
Deep Agents becomes valuable for planning, context management, tools, and
subagent delegation. It internally depends on LangChain and LangGraph, but this
standard does not use either framework directly. `store=False` keeps the direct
Responses example application-managed; agent persistence and provider storage
must be configured explicitly for the product's retention policy. Provider
model roles should be chosen deliberately rather than replacing lower-cost or
lower-latency routes with the flagship.

##### Required tests

Keep the deterministic provider cases above and add only the failure cases that
belong to the enabled product behavior. Test agent tools, delegation,
persistence, interrupts, and recovery through application outcomes instead of
asserting framework factory arguments. A real-provider smoke test is manual,
separately marked, and must never run in ordinary CI.

##### Related standards

- [pgvector](#recipesvectormd)
- [Chat streaming](#recipeschatmd)
- [SSE](#recipesssemd)
- [Security](#docssecuritymd)
- [Testing](#docstestingmd)

### recipes/sentry/README.md

#### Sentry

Error and performance monitoring, split into two composable modules:

- [`sentry-python`](#recipessentrysentry-pythonmd) — the `sentry-sdk` dependency itself.
  No framework integration; useful on its own for a plain script or worker
  process that wants manual `sentry_sdk.capture_exception` calls without
  Django wiring.
- [`sentry-django`](#recipessentrysentry-djangomd) — Django settings integration
  (`sentry_sdk.init(...)`, DSN/trace-rate environment variables). Requires
  `sentry-python`.

Neither module is required by any other module. `sentry-django` is included
in the `full` alias; request it explicitly (`--modules sentry-django`) to
add monitoring to a smaller module combination.

##### Related standards

See [reconstruction](#docsreconstructionmd) for how modules resolve,
and [settings](#srccoresettingssentrymd) for the `module_exists`
gating pattern this recipe follows.

### recipes/sentry/sentry-django.md

#### Sentry for Django

##### Purpose and when to use it

Use this module to report unhandled exceptions and request traces to Sentry
from the reconstructed Django project. It requires
[`sentry-python`](#recipessentrysentry-pythonmd).

##### When not to use it

Do not enable this module for a local-only reference reconstruction with no
Sentry project to send to — `SENTRY_DSN` defaults to empty, which makes
initialization a no-op, but the dependency and environment variables are
unnecessary weight if monitoring is never wired up.

##### Responsibilities and invariants

`src/core/settings/sentry.py` (a `base` artifact, unchanged by which modules
are selected) gates the entire `sentry_sdk.init(...)` call behind
`module_exists("sentry_sdk")`, the same pattern already used for
`django_celery_beat`, `django_celery_results`, and `channels_redis` — see
[settings](#srccoresettingssentrymd). This module contributes only
the dependency (via [`sentry-python`](#recipessentrysentry-pythonmd)) and the two
environment variables `sentry.py` reads; it owns no Python artifact of its
own, matching
[the rule that project aggregators stay owned by their top-level
standard](#recipesreadmemd).

`send_default_pii` stays `False`: never forward request bodies, headers, or
user PII to Sentry without an explicit, reviewed opt-in.

##### Complete canonical artifacts

<!-- dependency-fragment: .env.example#env; modules: sentry-django -->
```dotenv
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0
```

##### Alternatives and trade-offs

Gating on `module_exists("sentry_sdk")` rather than only on `SENTRY_DSN`
being set means a project that never selects this module never imports
`sentry_sdk` at all, instead of importing an unused dependency. A project
that selects the module but leaves `SENTRY_DSN` empty (e.g. local
development) still imports `sentry_sdk` but never calls `init`, which is a
deliberate compromise: it keeps `sentry.py` free of a third gating
condition beyond "is the package installed."

##### Required tests

Confirm `sentry_sdk.init` is not called when `SENTRY_DSN` is empty, is
called with the configured DSN and trace rate when set, and that importing
`settings` never raises when this module is excluded from the reconstruction
(sentry_sdk absent).

##### Related standards

See [sentry-python](#recipessentrysentry-pythonmd),
[settings](#srccoresettingssentrymd),
[environment](#environmentmd), and [security](#docssecuritymd).

### recipes/sentry/sentry-python.md

#### Sentry SDK

##### Purpose and when to use it

Use this module to add the `sentry-sdk` dependency without any Django
integration. It is the foundation [`sentry-django`](#recipessentrysentry-djangomd) builds
on, and is independently useful for a plain worker or script that wants to
call `sentry_sdk.capture_exception` manually.

##### When not to use it

Do not request this module alone if the goal is automatic Django error
capture — that requires `sentry-django`, which declares this module as a
requirement.

##### Responsibilities and invariants

This module owns exactly one thing: the `sentry-sdk` pin. It performs no
initialization; that is `sentry-django`'s responsibility so a plain-Python
consumer never pays for Django-specific setup.

##### Complete canonical artifacts

<!-- dependency-fragment: pyproject.toml#dependencies; modules: sentry-python -->
```toml
  "sentry-sdk[django]==2.66.1",
```

##### Alternatives and trade-offs

The `[django]` extra is pinned even for the framework-agnostic module
because this handbook only ever reconstructs Django projects; a non-Django
consumer of this handbook's pattern would drop the extra.

##### Required tests

Import `sentry_sdk` after reconstruction with no other Sentry configuration
present and confirm it does not raise.

##### Related standards

See [sentry-django](#recipessentrysentry-djangomd) and [settings](#srccoresettingssentrymd).

### recipes/sse.md

#### Ordered Server-Sent Events

##### Purpose and when to use it

Use SSE when a browser needs one-way, low-latency updates such as job progress
or assistant output. Events are persisted first, receive increasing IDs, and
can be replayed after reconnect with `Last-Event-ID`.

##### When not to use it

Use ordinary polling when updates are infrequent or operational simplicity is
more important than latency. Use WebSockets when the client must send
low-latency messages on the same connection. Do not hold synchronous WSGI
workers for long-lived streams.

##### Responsibilities and invariants

- The stream runs under ASGI.
- Every data event has a durable, increasing integer ID.
- Queries are account-scoped before filtering by ID.
- Reconnect starts strictly after the acknowledged `Last-Event-ID`.
- Heartbeat comments keep intermediaries from considering an idle stream dead.
- `asyncio.CancelledError` is re-raised after application cleanup.
- Reverse-proxy buffering is disabled and caching is prohibited.

##### Complete canonical artifacts

SSE and Channels share the `realtime` app. The model is intentionally a small
event log, not a general message broker.

<!-- artifact: src/apps/realtime/apps.py; profiles: realtime-sse,realtime,full -->
```python
from django.apps import AppConfig


class RealtimeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.realtime"
```

<!-- artifact: src/apps/realtime/models.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

from typing import ClassVar

from django.db import models

from apps.account.models import AccountOwnedModel


class StreamEvent(AccountOwnedModel):
    id = models.BigAutoField(primary_key=True)
    topic = models.CharField(max_length=120)
    event_type = models.CharField(max_length=80)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects: models.Manager[StreamEvent] = models.Manager()

    class Meta:
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "topic", "id"),
                name="stream_account_topic_idx",
            )
        ]
        ordering = ("id",)
```

<!-- artifact: src/apps/realtime/sse.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncGenerator, Awaitable, Callable

from asgiref.sync import sync_to_async

from apps.realtime.models import StreamEvent

DisconnectHandler = Callable[[], Awaitable[None]]


async def _no_disconnect_action() -> None:
    return None


def encode_event(event: StreamEvent) -> bytes:
    data = json.dumps(event.payload, separators=(",", ":"), ensure_ascii=False)
    lines = (
        f"id: {event.pk}",
        f"event: {event.event_type}",
        f"data: {data}",
        "",
        "",
    )
    return "\n".join(lines).encode()


@sync_to_async
def _next_events(
    *,
    account_id: object,
    topic: str,
    after_id: int,
    batch_size: int,
) -> list[StreamEvent]:
    return list(
        StreamEvent.objects.filter(
            account_id=account_id,
            topic=topic,
            id__gt=after_id,
        ).order_by("id")[:batch_size]
    )


async def event_stream(
    *,
    account_id: object,
    topic: str,
    after_id: int = 0,
    poll_interval: float = 0.5,
    heartbeat_interval: float = 15.0,
    on_disconnect: DisconnectHandler = _no_disconnect_action,
) -> AsyncGenerator[bytes]:
    cursor = after_id
    last_write = time.monotonic()
    try:
        while True:
            events = await _next_events(
                account_id=account_id,
                topic=topic,
                after_id=cursor,
                batch_size=100,
            )
            if events:
                for event in events:
                    cursor = event.pk
                    last_write = time.monotonic()
                    yield encode_event(event)
                continue

            now = time.monotonic()
            if now - last_write >= heartbeat_interval:
                last_write = now
                yield b": heartbeat\n\n"
            await asyncio.sleep(poll_interval)
    except asyncio.CancelledError:
        await on_disconnect()
        raise
```

<!-- artifact: src/apps/realtime/views.py; profiles: realtime-sse,realtime,full -->
```python
from __future__ import annotations

from django.http import StreamingHttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.realtime.sse import event_stream


def parse_last_event_id(raw_value: str | None) -> int:
    if raw_value is None or raw_value == "":
        return 0
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValidationError(
            {"Last-Event-ID": "Last-Event-ID must be a non-negative integer."}
        ) from error
    if value < 0:
        raise ValidationError({"Last-Event-ID": "Last-Event-ID must be a non-negative integer."})
    return value


class EventStreamView(APIView):
    def get(self, request: Request, topic: str) -> StreamingHttpResponse:
        after_id = parse_last_event_id(request.headers.get("Last-Event-ID"))
        response = StreamingHttpResponse(
            event_stream(
                account_id=request.user.account.pk,
                topic=topic,
                after_id=after_id,
            ),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache, no-transform"
        response["X-Accel-Buffering"] = "no"
        return response
```

<!-- artifact: src/apps/realtime/urls.py; profiles: realtime-sse,realtime,full -->
```python
from django.urls import path

from apps.realtime.views import EventStreamView

app_name = "realtime"

urlpatterns = [
    path("events/<slug:topic>/", EventStreamView.as_view(), name="event-stream"),
]
```

<!-- artifact: src/apps/realtime/tests/test_sse.py; profiles: realtime-sse,realtime,full -->
```python
import asyncio
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.account.models import Account
from apps.authentication.models import User
from apps.realtime.models import StreamEvent
from apps.realtime.sse import event_stream
from apps.realtime.views import parse_last_event_id


@patch("apps.realtime.views.event_stream")
@pytest.mark.django_db
def test_event_stream_endpoint_sets_streaming_headers(
    stream_factory: Mock,
    api_client: APIClient,
) -> None:
    # Arrange
    user = User.objects.create_user(email="http-events@example.test")
    Account.objects.create(user=user)
    api_client.force_authenticate(user=user)
    stream_factory.return_value = iter([b"event: heartbeat\n\n"])
    url = reverse("realtime:event-stream", kwargs={"topic": "jobs"})

    # Act
    response = api_client.get(url, HTTP_LAST_EVENT_ID="7")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "text/event-stream"
    assert response["Cache-Control"] == "no-cache, no-transform"
    assert response["X-Accel-Buffering"] == "no"
    stream_factory.assert_called_once_with(
        account_id=user.account.pk,
        topic="jobs",
        after_id=7,
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_stream_replays_ordered_account_events() -> None:
    # Arrange
    user = await User.objects.acreate(email="events@example.test")
    account = await Account.objects.acreate(user=user)
    other_user = await User.objects.acreate(email="other@example.test")
    other_account = await Account.objects.acreate(user=other_user)
    first = await StreamEvent.objects.acreate(
        account=account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 10},
    )
    second = await StreamEvent.objects.acreate(
        account=account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 20},
    )
    await StreamEvent.objects.acreate(
        account=other_account,
        topic="jobs",
        event_type="progress",
        payload={"percent": 99},
    )

    # Act
    stream = event_stream(account_id=account.pk, topic="jobs", poll_interval=0.01)
    first_chunk = await anext(stream)
    second_chunk = await anext(stream)
    await stream.aclose()

    # Assert
    assert first_chunk.startswith(f"id: {first.pk}\n".encode())
    assert second_chunk.startswith(f"id: {second.pk}\n".encode())
    assert b"99" not in first_chunk + second_chunk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_disconnect_runs_cleanup_and_propagates_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    user = await User.objects.acreate(email="cancel@example.test")
    account = await Account.objects.acreate(user=user)
    disconnected = asyncio.Event()
    clock = Mock()
    clock.monotonic.side_effect = (0.0, 61.0)
    monkeypatch.setattr("apps.realtime.sse.time", clock)

    async def cleanup() -> None:
        disconnected.set()

    stream = event_stream(
        account_id=account.pk,
        topic="idle",
        poll_interval=30,
        heartbeat_interval=60,
        on_disconnect=cleanup,
    )

    async def next_chunk() -> bytes:
        return await anext(stream)

    # Act
    heartbeat = await anext(stream)
    pending = asyncio.create_task(next_chunk())
    await asyncio.sleep(0)
    pending.cancel()

    # Assert
    with pytest.raises(asyncio.CancelledError):
        await pending
    assert heartbeat == b": heartbeat\n\n"
    assert disconnected.is_set()


def test_last_event_id_validation() -> None:
    # Arrange
    missing_cursor = None
    valid_cursor = "42"
    malformed_cursor = "not-a-number"
    negative_cursor = "-1"

    # Act
    initial_id = parse_last_event_id(missing_cursor)
    resumed_id = parse_last_event_id(valid_cursor)

    # Assert
    assert initial_id == 0
    assert resumed_id == 42
    with pytest.raises(ValidationError):
        parse_last_event_id(malformed_cursor)
    with pytest.raises(ValidationError):
        parse_last_event_id(negative_cursor)
```

##### Alternatives and trade-offs

A PostgreSQL event table makes replay deterministic but needs retention and
index maintenance. Redis Streams can provide replay at higher throughput but
introduce another durable cursor and tenant-scoping boundary. Plain pub/sub
has low latency but loses messages during disconnects, so clients still need a
database snapshot or recovery endpoint.

##### Required tests

Test response content type and proxy headers, ordered replay, account
isolation, malformed cursors, batches larger than 100, heartbeat timing,
disconnect cleanup, retention boundaries, slow clients, and application
shutdown. Run a smoke test with Daphne and a proxy configured exactly like
production.

##### Related standards

- [Channels](#recipeschannelsmd)
- [Celery module family](#recipesceleryreadmemd)
- [Chat streaming](#recipeschatmd)
- [Deployment](#recipesdeploymentmd)
- [API design](#docsapi-designmd)

### recipes/storage/storage-django.md

#### Private S3/MinIO Upload API

##### Purpose and when to use it

Use this module to expose [`storage-s3-core`](#recipesstoragestorage-s3-coremd)'s
upload/complete/delete lifecycle over DRF endpoints. Requires
`storage-s3-core`.

##### When not to use it

Proxy small uploads through Django when simplicity matters more than
web-worker bandwidth — that's a different endpoint shape than this direct
presigned-upload flow, not a reason to skip this module if the core lifecycle
is already selected.

##### Responsibilities and invariants

Every endpoint scopes its queryset (via the underlying service calls) to the
requesting account, matching every other tenant-owned resource in this
handbook.

##### Complete canonical artifacts

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

##### Alternatives and trade-offs

See [storage-s3-core](#recipesstoragestorage-s3-coremd) for the upload-transport
trade-offs; this module only adds the HTTP surface.

##### Required tests

Cover the full API lifecycle (start, complete, download, idempotent
delete) with a mocked S3 client; boundary and integration cases live in
[storage-s3-core](#recipesstoragestorage-s3-coremd).

##### Related standards

See [storage-s3-core](#recipesstoragestorage-s3-coremd), [API design](#docsapi-designmd),
and [security](#docssecuritymd).

### recipes/storage/storage-s3-core.md

#### Private S3/MinIO Upload Core

##### Purpose and when to use it

Use this module for private user files that should travel directly between
the client and an S3-compatible object store. It owns the `StoredFile`
record and the boto3-based presign/verify/delete lifecycle, independent of
how that lifecycle is exposed over HTTP (see [`storage-django`](#recipesstoragestorage-djangomd)
for the DRF views).

##### When not to use it

Do not use public buckets for private objects, trust a browser's reported
MIME type, accept a client-selected object key, or treat a successful
presign response as proof that an upload completed.

##### Responsibilities and invariants

- Object keys are server-generated, unpredictable, and account-prefixed.
- `start_upload` enforces an allowlist and maximum size.
- The signed POST enforces the same size and MIME constraints.
- `complete_upload` verifies object existence, exact size, content type, and
  ownership.
- Download and deletion always scope the database lookup to the account.
- Object deletion is idempotent and the row records deletion time.

##### Complete canonical artifacts

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

##### Alternatives and trade-offs

Presigned POST supports enforceable conditions and browser form uploads.
Presigned PUT has a simpler client shape but fewer policy conditions.
Multipart uploads are appropriate for very large objects and require durable
part state and abort cleanup. Malware scanning can move a verified object
from quarantine to a ready prefix before exposing download URLs.

##### Required tests

Use MinIO for integration tests. Cover exact boundary sizes, spoofed MIME
and metadata, missing objects, foreign-account identifiers, expired
signatures, path-like filenames, duplicate completion and deletion, private
bucket policy, download expiry, and cleanup of abandoned pending rows.

##### Related standards

See [storage-django](#recipesstoragestorage-djangomd), [security](#docssecuritymd),
and [operations](#docsoperationsmd).

### recipes/tenancy.md

#### Advanced Account Selection

##### Purpose and when to use it

Use this recipe when a user may belong to more than one account. A membership
row records authorization; selecting an account only chooses which already
authorized membership applies to the request.

For machine clients, an `X-Account-ID` header is explicit and stateless. For an
interactive client, a persisted preference can supply the account when the
header is absent. The header always wins, and neither mechanism grants access.

##### When not to use it

Keep the base project's one-account-per-user relationship when switching
accounts is not a real requirement. Do not infer an account from an
untrusted object identifier, an email domain, or the first account found in
the database.

##### Responsibilities and invariants

- A user can have at most one membership in an account.
- Only active memberships in active accounts can be selected.
- A persisted selection must still be re-authorized on every request.
- Account-owned querysets are scoped before lookup, update, or deletion.
- A missing header may use the persisted preference; an invalid explicit
  header is rejected and never falls back silently.
- Services perform selection changes; views consume the resolved context.

##### Complete canonical artifacts

The optional membership model and resolver are included only in the integrated
`full` teaching profile.

<!-- artifact: src/apps/membership/apps.py; profiles: tenancy-advanced,full -->
```python
from django.apps import AppConfig


class MembershipConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.membership"
```

<!-- artifact: src/apps/membership/models.py; profiles: tenancy-advanced,full -->
```python
from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MEMBER = "member", "Member"

    account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=16, choices=Role, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    objects: models.Manager[Membership] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("account", "user"),
                name="membership_unique_account_user",
            )
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("user", "is_active", "account"),
                name="membership_user_active_idx",
            )
        ]


class AccountPreference(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_preference",
    )
    current_account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="selected_by",
    )
    objects: models.Manager[AccountPreference] = models.Manager()
```

<!-- artifact: src/apps/membership/services.py; profiles: tenancy-advanced,full -->
```python
from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.account.models import Account
from apps.membership.models import AccountPreference, Membership


@dataclass(frozen=True, slots=True)
class AccountContext:
    account: Account
    membership: Membership


def _parse_account_id(raw_account_id: str) -> int:
    try:
        account_id = int(raw_account_id)
    except (TypeError, ValueError) as error:
        raise ValidationError({"account": "X-Account-ID must be a positive integer."}) from error
    if account_id <= 0:
        raise ValidationError({"account": "X-Account-ID must be a positive integer."})
    return account_id


def resolve_account_context(
    *,
    user: AbstractBaseUser,
    requested_account_id: str | None,
) -> AccountContext:
    if not user.is_authenticated:
        raise ValidationError({"account": "Authentication is required."})

    account_id: int | None
    if requested_account_id is not None:
        account_id = _parse_account_id(requested_account_id)
    else:
        account_id = (
            AccountPreference.objects.filter(user=user)
            .values_list("current_account_id", flat=True)
            .first()
        )
        if account_id is None:
            raise ValidationError({"account": "Select an account with X-Account-ID."})

    membership = (
        Membership.objects.select_related("account")
        .filter(
            user=user,
            account_id=account_id,
            is_active=True,
            account__is_active=True,
        )
        .first()
    )
    if membership is None:
        raise ValidationError({"account": "The account is not available."})
    return AccountContext(
        account=membership.account,
        membership=membership,
    )


@transaction.atomic
def persist_current_account(
    *,
    user: AbstractBaseUser,
    requested_account_id: str,
) -> AccountPreference:
    context = resolve_account_context(
        user=user,
        requested_account_id=requested_account_id,
    )
    preference, _created = AccountPreference.objects.update_or_create(
        user=user,
        defaults={"current_account": context.account},
    )
    return preference
```

<!-- artifact: src/apps/membership/mixins.py; profiles: tenancy-advanced,full -->
```python
from __future__ import annotations

from typing import Any

from rest_framework.request import Request

from apps.membership.services import AccountContext, resolve_account_context


class AccountContextMixin:
    account_context: AccountContext

    def initial(self, request: Request, *args: Any, **kwargs: Any) -> None:
        super().initial(  # ty: ignore[unresolved-attribute]  # DRF supplies initial through the view MRO.
            request, *args, **kwargs
        )
        self.account_context = resolve_account_context(
            user=request.user,
            requested_account_id=request.headers.get("X-Account-ID"),
        )
```

<!-- artifact: src/apps/membership/tests/test_selection.py; profiles: tenancy-advanced,full -->
```python
import pytest
from django.core.exceptions import ValidationError

from apps.account.models import Account
from apps.authentication.models import User
from apps.membership.models import AccountPreference, Membership
from apps.membership.services import persist_current_account, resolve_account_context


@pytest.mark.django_db
def test_explicit_account_must_belong_to_user() -> None:
    # Arrange
    user = User.objects.create_user(email="member@example.test", password="safe-pass-123")
    other = User.objects.create_user(email="other@example.test", password="safe-pass-123")
    allowed_account = Account.objects.create(user=user)
    denied_account = Account.objects.create(user=other)
    Membership.objects.create(user=user, account=allowed_account)

    # Act
    context = resolve_account_context(
        user=user,
        requested_account_id=str(allowed_account.pk),
    )

    # Assert
    with pytest.raises(ValidationError):
        resolve_account_context(
            user=user,
            requested_account_id=str(denied_account.pk),
        )
    assert context.account == allowed_account


@pytest.mark.django_db
def test_persisted_account_is_reauthorized() -> None:
    # Arrange
    user = User.objects.create_user(email="member@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    membership = Membership.objects.create(user=user, account=account)
    persist_current_account(user=user, requested_account_id=str(account.pk))

    # Act
    membership.is_active = False
    membership.save(update_fields=("is_active", "updated_at"))
    preference_exists = AccountPreference.objects.filter(
        user=user,
        current_account=account,
    ).exists()

    # Assert
    with pytest.raises(ValidationError):
        resolve_account_context(user=user, requested_account_id=None)
    assert preference_exists
```

##### Alternatives and trade-offs

Header selection works well for APIs and concurrent browser tabs, but every
client call must send the header. A persisted preference is convenient for a
single interactive context, but two tabs can change one another's default. A
signed account claim in a short-lived access token is another option, but
switching requires token re-issuance and server-side membership checks are
still necessary for revocation.

##### Required tests

Test inactive users, accounts, and memberships; malformed identifiers;
cross-account object access; explicit-header precedence; concurrent preference
updates; and list, retrieve, update, and delete endpoints. Assert that a
forbidden identifier does not reveal whether the account exists.

##### Related standards

- [Architecture](#docsarchitecturemd)
- [API design](#docsapi-designmd)
- [Security](#docssecuritymd)
- [Customer example](#srcappscustomerreadmemd)

### recipes/vector.md

#### Tenant-Scoped pgvector Search

##### Purpose and when to use it

Use pgvector when semantic search belongs beside relational Django data and the
expected scale fits PostgreSQL operations. Documents and chunks remain normal
account-owned rows; vector distance only changes ranking.

##### When not to use it

Use PostgreSQL full-text search for exact terminology and filters that do not
benefit from semantic similarity. Choose a dedicated vector system when
measured corpus size, recall, ingestion throughput, or independent scaling
requires one. Do not add embeddings without an evaluation set.

##### Responsibilities and invariants

- The embedding model and database column use one explicit dimension: 1536.
- Ingestion validates every vector before persistence.
- Document and chunk rows both carry the owning account.
- Similarity queries scope the account before ordering by distance.
- The HNSW index uses cosine operator classes matching `CosineDistance`.
- Changing models or dimensions requires a versioned re-embedding migration.
- Raw document text is not sent to a provider without the product's data policy.

##### Complete canonical artifacts

<!-- artifact: src/apps/documents/apps.py; profiles: vector-pgvector,vector-ai,full -->
```python
from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.documents"
```

<!-- artifact: src/apps/documents/migrations/__init__.py; profiles: vector-pgvector,vector-ai,full -->
```python
"""Documents schema history."""
```

<!-- artifact: src/apps/documents/migrations/0001_initial.py; profiles: vector-pgvector,vector-ai,full -->
```python
import uuid

import django.db.models.deletion
from django.db import migrations, models
from pgvector.django import HnswIndex, VectorExtension, VectorField


def create_hnsw_index(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    table = schema_editor.quote_name("documents_documentchunk")
    index = schema_editor.quote_name("chunk_embedding_hnsw_idx")
    schema_editor.execute(
        f"CREATE INDEX {index} ON {table} "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def drop_hnsw_index(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    index = schema_editor.quote_name("chunk_embedding_hnsw_idx")
    schema_editor.execute(f"DROP INDEX IF EXISTS {index}")


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("account", "0002_initial"),
    ]

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("source_key", models.CharField(max_length=255)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="account.account",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("account", "source_key"),
                        name="document_unique_account_source",
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="DocumentChunk",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ordinal", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("embedding_model", models.CharField(max_length=80)),
                ("embedding", VectorField(dimensions=1536)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="account.account",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chunks",
                        to="documents.document",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["account", "document", "ordinal"],
                        name="chunk_account_document_idx",
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("document", "ordinal"),
                        name="chunk_unique_document_ordinal",
                    )
                ],
            },
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_hnsw_index,
                    reverse_code=drop_hnsw_index,
                )
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="documentchunk",
                    index=HnswIndex(
                        ef_construction=64,
                        fields=["embedding"],
                        m=16,
                        name="chunk_embedding_hnsw_idx",
                        opclasses=("vector_cosine_ops",),
                    ),
                )
            ],
        ),
    ]
```

<!-- artifact: src/apps/documents/models.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models
from pgvector.django import HnswIndex, VectorField

from apps.account.models import AccountOwnedModel

EMBEDDING_DIMENSIONS = 1536


class Document(AccountOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    source_key = models.CharField(max_length=255)
    objects: models.Manager[Document] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("account", "source_key"),
                name="document_unique_account_source",
            )
        ]


class DocumentChunk(AccountOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    ordinal = models.PositiveIntegerField()
    content = models.TextField()
    embedding_model = models.CharField(max_length=80)
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    objects: models.Manager[DocumentChunk] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("document", "ordinal"),
                name="chunk_unique_document_ordinal",
            )
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "document", "ordinal"),
                name="chunk_account_document_idx",
            ),
            HnswIndex(
                name="chunk_embedding_hnsw_idx",
                fields=("embedding",),
                m=16,
                ef_construction=64,
                opclasses=("vector_cosine_ops",),
            ),
        ]
```

<!-- artifact: src/apps/documents/services.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.account.models import Account
from apps.documents.models import (
    EMBEDDING_DIMENSIONS,
    Document,
    DocumentChunk,
)


class EmbeddingProvider(Protocol):
    model_name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        pass


def validate_embedding(vector: Sequence[float]) -> list[float]:
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValidationError(
            {"embedding": (f"Expected {EMBEDDING_DIMENSIONS} values, got {len(vector)}.")}
        )
    return [float(value) for value in vector]


@transaction.atomic
def replace_document_chunks(
    *,
    account: Account,
    document: Document,
    contents: Sequence[str],
    provider: EmbeddingProvider,
) -> list[DocumentChunk]:
    if (
        document.account_id  # ty: ignore[unresolved-attribute]  # Django creates the FK id descriptor.
        != account.pk
    ):
        raise ValidationError({"document": "Document does not belong to the account."})
    if not contents or any(not content.strip() for content in contents):
        raise ValidationError({"contents": "Every chunk must contain text."})

    embeddings = provider.embed(contents)
    if len(embeddings) != len(contents):
        raise ValidationError({"embeddings": "Provider returned an unexpected number of vectors."})

    DocumentChunk.objects.filter(account=account, document=document).delete()
    chunks = [
        DocumentChunk(
            account=account,
            document=document,
            ordinal=ordinal,
            content=content,
            embedding_model=provider.model_name,
            embedding=validate_embedding(embedding),
        )
        for ordinal, (content, embedding) in enumerate(zip(contents, embeddings, strict=True))
    ]
    return DocumentChunk.objects.bulk_create(chunks)
```

<!-- artifact: src/apps/documents/selectors.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Sequence

from django.db.models import QuerySet
from pgvector.django import CosineDistance

from apps.account.models import Account
from apps.documents.models import DocumentChunk
from apps.documents.services import validate_embedding


def similar_chunks(
    *,
    account: Account,
    query_embedding: Sequence[float],
    limit: int = 10,
) -> QuerySet[DocumentChunk]:
    bounded_limit = max(1, min(limit, 50))
    vector = validate_embedding(query_embedding)
    return (
        DocumentChunk.objects.filter(account=account)
        .select_related("document")
        .annotate(distance=CosineDistance("embedding", vector))
        .order_by("distance", "id")[:bounded_limit]
    )
```

<!-- artifact: src/apps/documents/tests/test_search.py; profiles: vector-pgvector,vector-ai,full -->
```python
from collections.abc import Sequence

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from apps.account.models import Account
from apps.authentication.models import User
from apps.documents.models import EMBEDDING_DIMENSIONS, Document
from apps.documents.selectors import similar_chunks
from apps.documents.services import replace_document_chunks, validate_embedding


class DeterministicEmbeddings:
    model_name = "test-embedding-1536"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for index, _text in enumerate(texts):
            vector = [0.0] * EMBEDDING_DIMENSIONS
            vector[index % EMBEDDING_DIMENSIONS] = 1.0
            vectors.append(vector)
        return vectors


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="pgvector cosine distance requires PostgreSQL",
)
@pytest.mark.django_db
def test_search_never_returns_another_accounts_chunks() -> None:
    # Arrange
    user = User.objects.create_user(email="vectors@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    other_user = User.objects.create_user(
        email="other-vectors@example.test",
        password="safe-pass-123",
    )
    other_account = Account.objects.create(user=other_user)
    document = Document.objects.create(
        account=account,
        title="Guide",
        source_key="guide",
    )
    other_document = Document.objects.create(
        account=other_account,
        title="Private",
        source_key="private",
    )
    provider = DeterministicEmbeddings()
    replace_document_chunks(
        account=account,
        document=document,
        contents=["customer account guidance"],
        provider=provider,
    )
    replace_document_chunks(
        account=other_account,
        document=other_document,
        contents=["another account content"],
        provider=provider,
    )

    # Act
    result = list(
        similar_chunks(
            account=account,
            query_embedding=provider.embed(["customer"])[0],
        )
    )

    # Assert
    assert len(result) == 1
    assert result[0].account_id == account.pk


def test_embedding_dimension_is_explicit() -> None:
    # Arrange
    embedding = [0.0, 1.0]

    # Assert
    with pytest.raises(ValidationError):
        validate_embedding(embedding)
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: vector-pgvector -->
```toml
  "pgvector==0.5.0",
```

##### Alternatives and trade-offs

HNSW offers fast approximate search and good query latency at the cost of more
memory and slower writes. IVFFlat needs representative training data and
careful list and probe tuning. Exact search is a useful correctness baseline
for small corpora and recall evaluations. Hybrid semantic plus PostgreSQL
full-text ranking often outperforms either signal alone.

##### Required tests

Run against the `pgvector` extension, not SQLite. Test dimension rejection,
cross-account denial, stable tie ordering, empty corpora, maximum result limits,
transaction rollback during replacement, index creation, query plans at
representative scale, and measured approximate recall against exact cosine
search.

##### Related standards

- [OpenAI and Deep Agents](#recipesopenai-deep-agentsmd)
- [Architecture](#docsarchitecturemd)
- [Testing](#docstestingmd)

### source-map.md

#### Original Source Map

##### Purpose

This ledger accounts for every one of the 91 paths tracked by the executable
repository before its conversion to a Markdown-only standards handbook. Each
original path appears exactly once.

The allowed dispositions are:

- **converted**: the implementation keeps a path-shaped Markdown standard;
- **merged into an index**: an empty package marker is represented by its
  directory handbook index;
- **safely replaced**: the old concern is covered by a safer or more generic
  standard at a different path;
- **removed as empty/generated**: an empty placeholder or retired generated
  fixture has no canonical implementation;
- **generated at reconstruction**: an ordinary schema migration is mechanically
  derivable from its app's models and is produced by running `makemigrations`
  against a materialized profile rather than carried as a canonical artifact;
  see [reconstruction](#docsreconstructionmd).

Cookiecutter generation is retired. Its fixtures are not active commands or
templates. The former `.env.local` is safely replaced by the placeholder-only
`.env.example` artifact in `environment.md`; no secret or local value was
copied.

##### Path accounting

| # | Original tracked path | Disposition | Handbook location or rationale |
| ---: | --- | --- | --- |
| 1 | `.env.local` | safely replaced | `environment.md` documents a placeholder-only `.env.example` artifact |
| 2 | `.gitignore` | converted | `gitignore.md` |
| 3 | `.pre-commit-config.yaml` | converted | `pre-commit-config.md` |
| 4 | `.python-version` | converted | `python-version.md` |
| 5 | `.vscode/launch.json` | converted | `.vscode/launch.md` |
| 6 | `.vscode/settings.json` | converted | `.vscode/settings.md` |
| 7 | `CLAUDE.md` | safely replaced | `AGENTS.md` is the tool-neutral contribution and agent guide |
| 8 | `Dockerfile` | converted | `dockerfile.md` |
| 9 | `Makefile` | converted | `makefile.md` |
| 10 | `README.md` | converted | `README.md` is the handbook entry point |
| 11 | `conftest.py` | converted | `conftest.md` |
| 12 | `docker-compose-dev.yml` | converted | `compose-dev.md` |
| 13 | `docker-compose.yml` | converted | `compose.md` |
| 14 | `gunicorn.conf.py` | converted | `gunicorn.conf.md` |
| 15 | `pyproject.toml` | converted | `pyproject.md` |
| 16 | `pytest.ini` | converted | `pytest.md` |
| 17 | `scripts/channels-worker.sh` | converted | `scripts/channels-worker.md` |
| 18 | `scripts/channels.sh` | converted | `scripts/channels.md` |
| 19 | `scripts/webserver.sh` | converted | `scripts/webserver.md` |
| 20 | `scripts/worker.sh` | converted | `scripts/worker.md` |
| 21 | `src/apps/__init__.py` | merged into an index | `src/apps/README.md` |
| 22 | `src/apps/account/__init__.py` | merged into an index | `src/apps/account/README.md` |
| 23 | `src/apps/account/admin.py` | converted | `src/apps/account/admin.md` |
| 24 | `src/apps/account/apps.py` | converted | `src/apps/account/apps.md` |
| 25 | `src/apps/account/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 26 | `src/apps/account/migrations/0002_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 27 | `src/apps/account/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 28 | `src/apps/account/models.py` | converted | `src/apps/account/models.md` |
| 29 | `src/apps/account/services.py` | converted | `src/apps/account/services.md` |
| 30 | `src/apps/account/tests.py` | removed as empty/generated | Empty placeholder superseded by focused test modules |
| 31 | `src/apps/account/views.py` | removed as empty/generated | Empty placeholder; account behavior is exposed through authentication and scoped resources |
| 32 | `src/apps/api/__init__.py` | merged into an index | `src/apps/api/README.md` |
| 33 | `src/apps/api/apps.py` | converted | `src/apps/api/apps.md` |
| 34 | `src/apps/api/conftest.py` | removed as empty/generated | Empty placeholder; shared fixtures live in `src/apps/conftest.md` |
| 35 | `src/apps/api/exceptions.py` | converted | `src/apps/api/exceptions.md` |
| 36 | `src/apps/api/health.py` | converted | `src/apps/api/health.md` |
| 37 | `src/apps/api/pagination.py` | converted | `src/apps/api/pagination.md` |
| 38 | `src/apps/api/tests/__init__.py` | merged into an index | `src/apps/api/tests/README.md` |
| 39 | `src/apps/api/tests/views/test_auth_urls.py` | removed as empty/generated | Route-name assertions duplicated Django's resolver behavior without testing an application outcome |
| 40 | `src/apps/api/tests/views/test_health.py` | converted | `src/apps/api/tests/views/test_health.md` |
| 41 | `src/apps/api/urls.py` | converted | `src/apps/api/urls.md` |
| 42 | `src/apps/api/views.py` | converted | `src/apps/api/views.md` |
| 43 | `src/apps/authentication/__init__.py` | merged into an index | `src/apps/authentication/README.md` |
| 44 | `src/apps/authentication/admin.py` | converted | `src/apps/authentication/admin.md` |
| 45 | `src/apps/authentication/apps.py` | converted | `src/apps/authentication/apps.md` |
| 46 | `src/apps/authentication/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 47 | `src/apps/authentication/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 48 | `src/apps/authentication/models.py` | converted | `src/apps/authentication/models.md` |
| 49 | `src/apps/authentication/serializers.py` | converted | `src/apps/authentication/serializers.md` |
| 50 | `src/apps/authentication/services.py` | converted | `src/apps/authentication/services.md` |
| 51 | `src/apps/authentication/tests/__init__.py` | merged into an index | `src/apps/authentication/tests/README.md` |
| 52 | `src/apps/authentication/tests/helpers.py` | converted | `src/apps/authentication/tests/helpers.md` |
| 53 | `src/apps/authentication/tests/test_me.py` | converted | `src/apps/authentication/tests/test_me.md` |
| 54 | `src/apps/authentication/tests/test_meta.py` | safely replaced | `src/apps/authentication/tests/test_tokens.md` names and tests the JWT lifecycle behavior directly |
| 55 | `src/apps/authentication/tests/test_register.py` | converted | `src/apps/authentication/tests/test_register.md` |
| 56 | `src/apps/authentication/urls.py` | converted | `src/apps/authentication/urls.md` |
| 57 | `src/apps/authentication/views.py` | converted | `src/apps/authentication/views.md` |
| 58 | `src/apps/common/__init__.py` | merged into an index | `src/apps/common/README.md` |
| 59 | `src/apps/common/apps.py` | converted | `src/apps/common/apps.md` |
| 60 | `src/apps/common/exceptions.py` | converted | `src/apps/common/exceptions.md` |
| 61 | `src/apps/common/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 62 | `src/apps/common/models.py` | converted | `src/apps/common/models.md` |
| 63 | `src/apps/common/serializers.py` | removed as empty/generated | Empty placeholder; serializers remain within their owning applications |
| 64 | `src/apps/common/tests.py` | removed as empty/generated | Empty placeholder; tests remain within their owning applications |
| 65 | `src/apps/conftest.py` | converted | `src/apps/conftest.md` |
| 66 | `src/apps/customer/__init__.py` | merged into an index | `src/apps/customer/README.md` |
| 67 | `src/apps/customer/admin.py` | converted | `src/apps/customer/admin.md` |
| 68 | `src/apps/customer/apps.py` | converted | `src/apps/customer/apps.md` |
| 69 | `src/apps/customer/migrations/0001_initial.py` | generated at reconstruction | Ordinary migration; regenerate with `makemigrations` |
| 70 | `src/apps/customer/migrations/__init__.py` | generated at reconstruction | Package marker created alongside the regenerated migrations |
| 71 | `src/apps/customer/models.py` | converted | `src/apps/customer/models.md` |
| 72 | `src/apps/customer/serializers.py` | converted | `src/apps/customer/serializers.md` |
| 73 | `src/apps/customer/services.py` | converted | `src/apps/customer/services.md` |
| 74 | `src/apps/customer/tests/__init__.py` | merged into an index | `src/apps/customer/tests/README.md` |
| 75 | `src/apps/customer/tests/helpers.py` | converted | `src/apps/customer/tests/helpers.md` |
| 76 | `src/apps/customer/tests/test_views.py` | converted | `src/apps/customer/tests/test_views.md` |
| 77 | `src/apps/customer/urls.py` | converted | `src/apps/customer/urls.md` |
| 78 | `src/apps/customer/views.py` | converted | `src/apps/customer/views.md` |
| 79 | `src/core/__init__.py` | converted | `src/core/__init__.md` |
| 80 | `src/core/asgi.py` | converted | `src/core/asgi.md` |
| 81 | `src/core/celery.py` | converted | `src/core/celery.md` |
| 82 | `src/core/settings.py` | converted | `src/core/settings/README.md` (split into a settings package; see `src/core/settings/*.md`) |
| 83 | `src/core/urls.py` | converted | `src/core/urls.md` |
| 84 | `src/core/wsgi.py` | converted | `src/core/wsgi.md` |
| 85 | `src/manage.py` | converted | `src/manage.md` |
| 86 | `tests/conftest.py` | converted | `tests/conftest.md` |
| 87 | `tests/fixtures/cookiecutter-basic/cookiecutter.json` | safely replaced | `docs/reconstruction.md` defines profile reconstruction without templates |
| 88 | `tests/fixtures/cookiecutter-basic/{{cookiecutter.project_slug}}/README.md` | safely replaced | `docs/reconstruction.md` defines safe derived output without template variables |
| 89 | `tests/test_healthcheck.py` | converted | `tests/test_healthcheck.md` |
| 90 | `todo.md` | safely replaced | `README.md` navigation and `docs/testing.md` acceptance criteria replace the placeholder list |
| 91 | `uv.lock` | converted | `uv-lock.md` |

##### Verification

Compare the second column of the table with the frozen original path list. The
set must match exactly, with 91 table rows, no duplicate original path, and no
omission. Repository validation also confirms that each listed handbook
location is either present or intentionally described as removed.
