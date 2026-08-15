# Sentry for Django

## Purpose and when to use it

Use this module to report unhandled exceptions and request traces to Sentry
from the reconstructed Django project. It requires
[`sentry-python`](sentry-python.md).

## When not to use it

Do not enable this module for a local-only reference reconstruction with no
Sentry project to send to — `SENTRY_DSN` defaults to empty, which makes
initialization a no-op, but the dependency and environment variables are
unnecessary weight if monitoring is never wired up.

## Responsibilities and invariants

`src/core/settings/sentry.py` (a `base` artifact, unchanged by which modules
are selected) gates the entire `sentry_sdk.init(...)` call behind
`module_exists("sentry_sdk")`, the same pattern already used for
`django_celery_beat`, `django_celery_results`, and `channels_redis` — see
[settings](../../src/core/settings/sentry.md). This module contributes only
the dependency (via [`sentry-python`](sentry-python.md)) and the two
environment variables `sentry.py` reads; it owns no Python artifact of its
own, matching
[the rule that project aggregators stay owned by their top-level
standard](../README.md).

`send_default_pii` stays `False`: never forward request bodies, headers, or
user PII to Sentry without an explicit, reviewed opt-in.

## Complete canonical artifacts

<!-- dependency-fragment: .env.example#env; modules: sentry-django -->
```dotenv
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0
```

## Alternatives and trade-offs

Gating on `module_exists("sentry_sdk")` rather than only on `SENTRY_DSN`
being set means a project that never selects this module never imports
`sentry_sdk` at all, instead of importing an unused dependency. A project
that selects the module but leaves `SENTRY_DSN` empty (e.g. local
development) still imports `sentry_sdk` but never calls `init`, which is a
deliberate compromise: it keeps `sentry.py` free of a third gating
condition beyond "is the package installed."

## Required tests

Confirm `sentry_sdk.init` is not called when `SENTRY_DSN` is empty, is
called with the configured DSN and trace rate when set, and that importing
`settings` never raises when this module is excluded from the reconstruction
(sentry_sdk absent).

## Related standards

See [sentry-python](sentry-python.md),
[settings](../../src/core/settings/sentry.md),
[environment](../../environment.md), and [security](../../docs/security.md).
