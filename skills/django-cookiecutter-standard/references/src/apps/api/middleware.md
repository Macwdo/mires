# Request ID middleware

## Purpose and when to use it

Assign one correlation identifier to every HTTP request and return it in the
`X-Request-ID` response header.

## When not to use it

Do not treat a caller-supplied request ID as authentication or authorization.

## Responsibilities and invariants

Only short identifiers containing conservative visible characters are trusted;
all other values are replaced with a random UUID.

## Complete canonical artifact

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

## Alternatives and trade-offs

Always generating a server ID avoids untrusted input but breaks correlation
across a trusted gateway. Validation preserves that chain without accepting
arbitrary header content.

## Required tests

Test generated, accepted, rejected, and response-propagated identifiers.

## Related standards

- [Error envelopes](exceptions.md)
