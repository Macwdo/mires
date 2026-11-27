# Authentication API views

## Purpose and when to use it

Expose registration, the current authenticated user, and explicit refresh-token
revocation.

## When not to use it

Do not build custom access-token parsing or refresh rotation in these views.

## Responsibilities and invariants

Public registration has no authentication class, uses a stricter named
throttle scope, returns all user output through an allow-list serializer, and
fails malformed logout tokens safely.

## Complete canonical artifact

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

## Alternatives and trade-offs

Server-side sessions make revocation immediate. Short access tokens plus rotated
and blacklisted refresh tokens preserve stateless API authentication while
bounding revocation delay. Small subclasses are preferable to passing undeclared
attributes to `as_view()`, which Django rejects.

## Required tests

Cover public registration, authenticated `me`, invalid logout tokens, and
blacklisted refresh-token rejection.

## Related standards

- [URL surface](urls.md)
- [JWT tests](tests/test_tokens.md)
