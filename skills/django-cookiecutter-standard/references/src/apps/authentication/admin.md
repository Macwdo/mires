# Custom user administration

## Purpose and when to use it

Give authorized staff a safe interface for email-based users.

## When not to use it

Do not expose the Django admin to end users or use it as a public account API.

## Responsibilities and invariants

Password changes use Django's hashed-password form and email remains the login
identifier.

## Complete canonical artifact

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

## Alternatives and trade-offs

A separate staff portal supports tighter workflows but duplicates mature admin
security and form behavior.

## Required tests

Smoke-test user creation and change views with an authorized staff client.

## Related standards

- [User model](models.md)
