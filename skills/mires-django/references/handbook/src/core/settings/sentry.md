# Sentry Initialization

## Purpose and when to use it

Use this module to initialize `sentry_sdk` when the
[`sentry-django`](../../../recipes/sentry/sentry-django.md) module is part
of the resolved reconstruction.

## When not to use it

Do not import `sentry_sdk` unconditionally; a base reconstruction that
excludes the `sentry-django` module never installs the package.

## Responsibilities and invariants

Initialization is gated by `module_exists("sentry_sdk")`, so this module
stays importable whether or not `sentry-sdk` is installed. `SENTRY_DSN`
empty is a valid, fully local configuration: the SDK is imported but never
initialized.

## Complete canonical artifact

<!-- artifact: src/core/settings/sentry.py; profiles: base -->
```python
from decouple import config

from .base import ENVIRONMENT, module_exists

if module_exists("sentry_sdk"):
    import sentry_sdk

    SENTRY_DSN = config("SENTRY_DSN", default="")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            send_default_pii=False,
            traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=0, cast=float),
        )
```

## Required tests

Settings import without `sentry-sdk` installed; settings import with it
installed and `SENTRY_DSN` unset does not call `sentry_sdk.init`.

## Related standards

See [base](base.md) and [sentry](../../../recipes/sentry/README.md).
