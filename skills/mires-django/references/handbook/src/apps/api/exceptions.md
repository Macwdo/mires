# Consistent API exception handling

## Purpose and when to use it

Configure this handler as DRF's global `EXCEPTION_HANDLER` to normalize all API
errors.

## When not to use it

Do not return raw exception strings, tracebacks, SQL, or configuration values.

## Responsibilities and invariants

Every error contains a stable code, human-readable message, structured details,
and the request ID. Unexpected errors are logged and returned as a generic 500.

## Complete canonical artifact

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

## Alternatives and trade-offs

RFC 9457 problem details is a good interoperable alternative. This smaller
envelope keeps the example explicit and stable for clients.

## Required tests

Cover validation, authentication, not-found, domain, and unexpected exceptions;
assert internal messages never leak.

## Related standards

- [Request IDs](middleware.md)
- [Domain exceptions](../common/exceptions.md)
