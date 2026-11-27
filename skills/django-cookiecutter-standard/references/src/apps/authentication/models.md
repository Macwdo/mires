# Email-based custom user

## Purpose and when to use it

Use this model when email is the sole login identifier from the start of a
project.

## When not to use it

Do not swap user models after a deployed database already references Django's
default user.

## Responsibilities and invariants

- `username` is removed rather than mirrored from email.
- Manager methods normalize email and hash passwords.
- Superuser creation rejects contradictory privilege flags.

## Complete canonical artifact

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

## Alternatives and trade-offs

Subclassing `AbstractUser` retains Django permissions and admin behavior. A
smaller `AbstractBaseUser` model offers more control but requires more security
plumbing.

## Required tests

Test email normalization, password hashing, duplicate rejection, and superuser
flag validation.

## Related standards

- [Migration generation](../../../docs/reconstruction.md#migration-generation)
- [User administration](admin.md)
