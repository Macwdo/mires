# Safe domain exceptions

## Purpose and when to use it

Raise these exceptions when an authenticated request cannot operate in its
account context.

## When not to use it

Do not expose database errors or internal exception messages through new
`APIException` subclasses.

## Responsibilities and invariants

Each exception has a stable code, an appropriate HTTP status, and a public
message that contains no sensitive state.

## Complete canonical artifact

<!-- artifact: src/apps/common/exceptions.py; profiles: base,full -->
```python
from rest_framework import status
from rest_framework.exceptions import APIException


class AccountUnavailable(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "The account is not available."
    default_code = "account_unavailable"
```

## Alternatives and trade-offs

Returning not-found can conceal resource existence. This exception is used only
for the caller's own inactive account; cross-account object lookups still
return not-found.

## Required tests

API tests assert both the status and the normalized error envelope.

## Related standards

- [API exception handler](../api/exceptions.md)
