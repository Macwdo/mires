---
name: mires-python-django
description: Apply Macwdo's typed Django and Django REST Framework standards for uv, Ruff, ty, models, migrations, selectors, services, serializers, endpoints, nested routers, authentication, testing, and operations. Use only when Django or DRF owns the application boundary.
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
uv add django djangorestframework drf-nested-routers
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

Do not annotate every Django model field redundantly when the assignment is already clear. Concentrate annotations at public boundaries and dynamic framework extension points.

### Typed QuerySet, Selector, And Service

```python
from __future__ import annotations

from typing import Self, TypedDict

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


class CustomerCreateData(TypedDict):
    name: str


def customer_list(*, owner: AbstractBaseUser) -> QuerySet[Customer]:
    return Customer.objects.active().filter(owner=owner)


@transaction.atomic
def customer_create(
    *,
    owner: AbstractBaseUser,
    data: CustomerCreateData,
) -> Customer:
    return Customer.objects.create(owner=owner, **data)
```

Use the repository's concrete user model type when available. Keep DTOs at service/API boundaries; do not duplicate a serializer schema and a `TypedDict` unless both have real consumers.

### Typed DRF Boundary

```python
from typing import Any

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

    def create(self, validated_data: dict[str, Any]) -> Customer:
        request = self.context["request"]
        data: CustomerCreateData = {"name": validated_data["name"]}
        return customer_create(owner=request.user, data=data)


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

`dict[str, Any]` is acceptable at DRF's dynamic validated-data boundary; narrow it before calling domain code. Do not spread `Any` through selectors and services.

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
from typing import Any

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
    def create(self, validated_data: dict[str, Any]) -> Customer:
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
from typing import Any

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
    def create(self, validated_data: dict[str, Any]) -> Invoice:
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
from collections.abc import Callable, Mapping
from typing import Any, Generic, TypeVar, cast

from django.db.models import Model, QuerySet
from rest_framework import serializers


_ModelT = TypeVar("_ModelT", bound=Model)
ContextQueryset = Callable[[Mapping[str, Any]], QuerySet[_ModelT]]


class ContextPrimaryKeyRelatedField(
    serializers.PrimaryKeyRelatedField,
    Generic[_ModelT],
):
    queryset: QuerySet[_ModelT] | ContextQueryset[_ModelT] | None

    def get_queryset(self) -> QuerySet[_ModelT] | None:
        queryset = self.queryset
        if callable(queryset):
            return queryset(self.context)
        return cast(QuerySet[_ModelT] | None, super().get_queryset())
```

The reusable field has no custom `__init__`, no owner assumptions, and no lookup DSL. The domain function owns the actual queryset:

```python
from collections.abc import Mapping
from typing import Any

from django.db.models import QuerySet

from .models import BillingProfile


def billing_profiles_for_context(
    context: Mapping[str, Any],
) -> QuerySet[BillingProfile]:
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
invoice = serializer.save(owner=request.user)
```

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
from typing import Any


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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        has_nested = "customer_profile" in attrs
        has_id = "selected_customer_profile" in attrs

        if has_nested == has_id:
            raise serializers.ValidationError(
                "Provide exactly one of customer_profile or customer_profile_id."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Invoice:
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
from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def given_a_customer(
    *,
    api_client: APIClient,
    name: str = "Ada Lovelace",
    email: str = "ada@example.test",
    profile: dict[str, Any] | None = None,
    addresses: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
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
) -> dict[str, Any]:
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
- Do not hide write-side business logic in views, serializers, managers, querysets, model `save()`, or signals.
- If a service becomes read-heavy and stops mutating state, move the fetch logic into a selector.
- Start with `services.py`; split into a `services/` package only when the app grows multiple service domains.

---

### Django Services Dependencies

Use this section when a Django service needs other services, selectors, tasks, repositories, or external clients.

#### Rules

- Pass external clients and configurable collaborators as arguments instead of instantiating them deep in the service.
- Call selectors for read-heavy checks or visibility queries instead of duplicating fetch logic.
- Allow services to call model methods, external clients, and async tasks when those are explicit dependencies.
- Keep request and response objects out of services.
- Obtain SDK clients through the project dependency layer at the edge, then pass them into the service.

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
- Use a class only when the service represents a multi-step flow or needs a small namespace around shared dependencies.
- If the existing app already uses a `services/` package or class-based flow services, follow that local shape.
- Keep each method explicit, typed, and transaction-aware.
- Do not turn ordinary create/update/delete behavior into a class just for organization.

#### Example

```python
class ExampleExportService:
    def __init__(self, *, account) -> None:
        self.account = account

    @transaction.atomic
    def start(self, *, name: str) -> ExampleExport:
        export = ExampleExport(account=self.account, name=name, status="pending")
        export.full_clean()
        export.save()
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
