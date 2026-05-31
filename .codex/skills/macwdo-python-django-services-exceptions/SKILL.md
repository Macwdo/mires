---
name: macwdo-python-django-services-exceptions
description: "Macwdo Django service exception guidance. Use for apps.common.exceptions, BussinesLogicException-compatible domain errors, status codes, default_detail, default_code, and caller-friendly messages."
---

# Django Services Exceptions

Use this skill when service failures need a domain-specific exception or HTTP-facing translation.

## Rules

- Use exceptions from `apps.common.exceptions` when the project provides them.
- Raise explicit business exceptions with human-readable messages when an invariant fails.
- Add a new exception type in `apps/common/exceptions.py` when callers need a distinct status code or error code.
- Preserve the project spelling of existing base exception classes, including `BussinesLogicException` if that is what the repo defines.
- Do not hide invalid business state in booleans or `None` returns when callers need an actionable error.

## Example

```python
from apps.common.exceptions import BussinesLogicException


def do_something(*, instance) -> None:
    if not instance.is_valid:
        raise BussinesLogicException("Custom message")
```
