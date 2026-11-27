# Sentry

Error and performance monitoring, split into two composable modules:

- [`sentry-python`](sentry-python.md) — the `sentry-sdk` dependency itself.
  No framework integration; useful on its own for a plain script or worker
  process that wants manual `sentry_sdk.capture_exception` calls without
  Django wiring.
- [`sentry-django`](sentry-django.md) — Django settings integration
  (`sentry_sdk.init(...)`, DSN/trace-rate environment variables). Requires
  `sentry-python`.

Neither module is required by any other module. `sentry-django` is included
in the `full` alias; request it explicitly (`--modules sentry-django`) to
add monitoring to a smaller module combination.

## Related standards

See [reconstruction](../../docs/reconstruction.md) for how modules resolve,
and [settings](../../src/core/settings/sentry.md) for the `module_exists`
gating pattern this recipe follows.
