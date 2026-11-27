# Advanced Account Selection

## Purpose and when to use it

Use this recipe when a user may belong to more than one account. A membership
row records authorization; selecting an account only chooses which already
authorized membership applies to the request.

For machine clients, an `X-Account-ID` header is explicit and stateless. For an
interactive client, a persisted preference can supply the account when the
header is absent. The header always wins, and neither mechanism grants access.

## When not to use it

Keep the base project's one-account-per-user relationship when switching
accounts is not a real requirement. Do not infer an account from an
untrusted object identifier, an email domain, or the first account found in
the database.

## Responsibilities and invariants

- A user can have at most one membership in an account.
- Only active memberships in active accounts can be selected.
- A persisted selection must still be re-authorized on every request.
- Account-owned querysets are scoped before lookup, update, or deletion.
- A missing header may use the persisted preference; an invalid explicit
  header is rejected and never falls back silently.
- Services perform selection changes; views consume the resolved context.

## Complete canonical artifacts

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

## Alternatives and trade-offs

Header selection works well for APIs and concurrent browser tabs, but every
client call must send the header. A persisted preference is convenient for a
single interactive context, but two tabs can change one another's default. A
signed account claim in a short-lived access token is another option, but
switching requires token re-issuance and server-side membership checks are
still necessary for revocation.

## Required tests

Test inactive users, accounts, and memberships; malformed identifiers;
cross-account object access; explicit-header precedence; concurrent preference
updates; and list, retrieve, update, and delete endpoints. Assert that a
forbidden identifier does not reveal whether the account exists.

## Related standards

- [Architecture](../docs/architecture.md)
- [API design](../docs/api-design.md)
- [Security](../docs/security.md)
- [Customer example](../src/apps/customer/README.md)
