# Sentry SDK

## Purpose and when to use it

Use this module to add the `sentry-sdk` dependency without any Django
integration. It is the foundation [`sentry-django`](sentry-django.md) builds
on, and is independently useful for a plain worker or script that wants to
call `sentry_sdk.capture_exception` manually.

## When not to use it

Do not request this module alone if the goal is automatic Django error
capture — that requires `sentry-django`, which declares this module as a
requirement.

## Responsibilities and invariants

This module owns exactly one thing: the `sentry-sdk` pin. It performs no
initialization; that is `sentry-django`'s responsibility so a plain-Python
consumer never pays for Django-specific setup.

## Complete canonical artifacts

<!-- dependency-fragment: pyproject.toml#dependencies; modules: sentry-python -->
```toml
  "sentry-sdk[django]==2.66.1",
```

## Alternatives and trade-offs

The `[django]` extra is pinned even for the framework-agnostic module
because this handbook only ever reconstructs Django projects; a non-Django
consumer of this handbook's pattern would drop the extra.

## Required tests

Import `sentry_sdk` after reconstruction with no other Sentry configuration
present and confirm it does not raise.

## Related standards

See [sentry-django](sentry-django.md) and [settings](../../src/core/settings/sentry.md).
