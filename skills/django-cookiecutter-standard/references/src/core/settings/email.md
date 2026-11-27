# Email Configuration

## Purpose and when to use it

Use this module for the outbound email backend and default sender address.

## When not to use it

Do not send email directly from views or services with a hardcoded backend;
read `EMAIL_BACKEND` so tests and local runs use the console backend
automatically.

## Responsibilities and invariants

The default backend writes to the console, so no environment sends real
email without explicit configuration.

## Complete canonical artifact

<!-- artifact: src/core/settings/email.py; profiles: base -->
```python
from decouple import config

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@localhost")
```

## Required tests

Test that the default backend is the console backend and that outgoing
messages use `DEFAULT_FROM_EMAIL`.

## Related standards

See [base](base.md).
