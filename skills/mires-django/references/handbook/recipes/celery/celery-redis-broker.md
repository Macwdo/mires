# Celery Redis Broker

## Purpose and when to use it

Use this module to document the Redis broker/result-backend configuration
that `celery-core` and every module requiring it depend on. Requires only
`celery-core`.

## When not to use it

This module has no independent effect — it exists so "which modules need
Redis" is answerable without reading `celery-core`'s own doc. Requesting it
without `celery-core` is meaningless (and `celery-core` is pulled in
automatically since this module requires it).

## Responsibilities and invariants

This module owns no artifact of its own. The broker URL, result backend,
and Redis connection settings are aggregator-owned, exactly like every
other project-wide setting: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`,
and `REDIS_URL` live unconditionally in
[`src/core/settings/celery.py`](../../src/core/settings/celery.md) and
[`src/core/settings/channels.py`](../../src/core/settings/channels.md)
(`base` artifacts) and
[`.env.example`](../../environment.md) (also `base`), because a setting
module cannot vary per selected module the way feature code can — see
["project aggregators... remain owned by their top-level standards"](../README.md).
The `celery[redis]` dependency itself is pinned by `celery-core`'s own
dependency-fragment in [`src/core/celery.md`](../../src/core/celery.md),
since this template never uses Celery with a different broker.

## Alternatives and trade-offs

Bundling the `[redis]` extra into `celery-core` rather than giving this
module its own dependency-fragment avoids a package listed twice with
different extras; the cost is that a hypothetical non-Redis broker would
require editing `celery-core` directly rather than swapping this module out.

## Required tests

Covered by [celery-django](celery-django.md)'s worker-against-Redis
integration test; this module has no independent test surface.

## Related standards

See [the Celery application](../../src/core/celery.md),
[environment](../../environment.md), and
[the Celery module family](README.md).
