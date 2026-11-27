# API boundary

## Purpose and when to use it

Use this package for cross-cutting HTTP policy: versioned routing, request IDs,
error envelopes, health probes, authentication defaults, pagination, and
account-scoped view bases.

## When not to use it

Do not place domain models or business workflows in the API package.

## Responsibilities and invariants

- Authenticated endpoints deny requests without an active account.
- Errors have one stable envelope and include the request ID.
- Liveness performs no dependency I/O; readiness verifies the database.
- Pagination ordering is unique and stable.
- Default API throttling applies sustained and burst limits; sensitive routes
  add named scopes.

## Complete canonical artifact

<!-- artifact: src/apps/api/__init__.py; profiles: base,full -->
```python
"""Versioned API infrastructure."""
```

## Reusable burst throttle

Use a second user throttle with its own scope to constrain short bursts
independently from the sustained authenticated-user limit. For anonymous
requests, DRF's `UserRateThrottle` falls back to the client identifier, so the
burst policy also applies before authentication.

<!-- artifact: src/apps/api/throttling.py; profiles: base,full -->
```python
from rest_framework.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"
```

## Alternatives and trade-offs

Per-application HTTP helpers reduce central coupling but can fragment public
behavior. Only genuinely cross-cutting policy belongs here. Additional
`SimpleRateThrottle` subclasses are appropriate when a limit needs a different
identity key, but keys derived from email addresses or other submitted
identifiers must be normalized, non-enumerable, and privacy-reviewed.

## Required tests

Test health states, request ID propagation, envelope normalization,
authentication defaults, burst and scoped throttling, and inactive-account
denial.

## Related standards

- [API views](views.md)
- [Exception handling](exceptions.md)
- [Request IDs](middleware.md)
- [API design](../../../docs/api-design.md)
