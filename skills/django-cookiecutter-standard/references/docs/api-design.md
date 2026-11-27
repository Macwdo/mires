# API Design

## Purpose and when to use it

Use these defaults for authenticated JSON REST APIs.

## Responsibilities and invariants

JWT access tokens are short lived. Refresh tokens rotate and old refresh tokens are blacklisted. Registration never logs secrets and returns the same public user shape as `/auth/me/`.

Errors use one envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": {"email": ["Enter a valid email address."]},
    "request_id": "01J2N8Y5Q7M6R4T3V1W0X9Z8AB"
  }
}
```

The request ID is accepted only when syntactically safe; otherwise middleware generates one. It is returned in `X-Request-ID`, logged, and included in handled error responses.

Customer list endpoints support `search`, a small allowlist of ordering fields, and cursor pagination ordered by `-created_at,-id`. The unique tie-breaker is mandatory. Querysets are account-scoped before filtering.

## Throttling and rate limits

Apply rate limits in layers:

- `AnonRateThrottle` bounds unauthenticated traffic by DRF's client identifier.
- `UserRateThrottle` provides a sustained per-user limit and falls back to the
  client identifier before authentication.
- `BurstRateThrottle` uses a separate scope for short spikes.
- `ScopedRateThrottle` adds tighter limits to registration, token, refresh,
  verification, and resource-heavy endpoints through `throttle_scope`.

Every configured class is evaluated, so the strictest applicable limit wins.
Views that set `throttle_classes` replace the global list; prefer a
`throttle_scope` when the endpoint should retain global limits. Health probes
are the deliberate exception and set `throttle_classes = ()`.

Treat a DRF 429 response and its `Retry-After` header as part of the API
contract. Clients must use bounded exponential backoff with jitter and must not
retry non-idempotent requests blindly.

DRF throttles use Django's cache and non-atomic cache operations. Local-memory
caches count separately per worker and small request overruns are possible
under concurrency. Use a shared production cache, monitor 429 volume by scope,
and enforce denial-of-service, credential-stuffing, and volumetric controls at
the trusted edge. Configure DRF's `NUM_PROXIES` only for a fixed, trusted proxy
topology that strips spoofed forwarding headers; otherwise use the direct
remote address.

With Django's Redis cache backend and the `redis` package installed, the
production cache setting has this shape:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "TIMEOUT": 300,
    }
}
```

Keep local tests on `LocMemCache` unless they explicitly prove shared-cache
behavior. Never use Django's database cache as a high-traffic throttle store.

`/health/live/` only reports process liveness. `/health/ready/` verifies required dependencies and returns 503 when unavailable. Health responses disclose no credentials or internal exception details.

## Alternatives and trade-offs

Session authentication remains appropriate for same-origin browser applications. Page-number pagination is easier to navigate but is less stable under concurrent writes. Application throttling is intentionally approximate; exact quotas require an atomic quota service and a product-specific usage model.

## Required tests

Cover token rotation/revocation, unauthenticated denial, malformed input, stable cursors, request IDs, error envelopes, cross-account denial, isolated throttle identities, scoped 429 responses, `Retry-After`, and health-probe bypass.
