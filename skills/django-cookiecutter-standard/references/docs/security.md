# Security

## Purpose and when to use it

Apply this checklist to every reconstructed profile and deployment.

## Responsibilities and invariants

Production starts only with a non-placeholder `SECRET_KEY`, `DEBUG=false`, non-empty `ALLOWED_HOSTS`, an explicit database URL, and HTTPS-aware cookie/proxy settings. Run `manage.py check --deploy` in the release pipeline.

Tenant identity comes from authenticated server-side state, never from a request-body `account_id`. Scope before lookup so cross-account IDs produce the same not-found behavior as unknown IDs.

Application throttling limits routine abuse and protects fair use, but is not a denial-of-service boundary. Use a shared cache across application workers, apply stricter scopes to authentication and expensive operations, and enforce authoritative limits at the trusted proxy or API gateway. Trust forwarded client addresses only when the proxy strips inbound forwarding headers and direct application access is blocked.

Credentials are environment variables. The canonical `.env.example` contains placeholders only. Rotate leaked credentials rather than merely deleting them from Git.

Private upload flows validate tenant ownership, object key prefix, declared size, observed size, and an allowlist of MIME types. Presigned operations are short lived. Provider callbacks and task delivery are idempotent.

OpenAI examples send `store=False` and a stable pseudonymous `safety_identifier`. They never expose provider errors verbatim and never use a real key in tests.

## Required tests

Test production fail-fast behavior, deploy checks, JWT blacklisting, object-level isolation, throttle scopes and identity isolation, upload constraints, origin rejection, and secret scans.
