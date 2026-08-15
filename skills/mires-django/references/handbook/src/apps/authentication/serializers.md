# Authentication serializers

## Purpose and when to use it

Validate registration, current-user output, and refresh-token logout payloads.

## When not to use it

Token signature and claim validation belong to Simple JWT, not custom fields.

## Responsibilities and invariants

Passwords are write-only, Django password validators run with user context, and
email uniqueness errors are deterministic.

## Complete canonical artifact

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

## Alternatives and trade-offs

Confirm-password fields can catch client typing errors, but API clients can
perform that comparison locally without transmitting duplicate secrets.

## Required tests

Test normalization, duplicate email, weak password rejection, and that response
serialization excludes password fields.

## Related standards

- [Registration service](services.md)
- [Authentication views](views.md)
