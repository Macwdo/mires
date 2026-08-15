# Authentication and user identity

## Purpose and when to use it

Use this package for email-based identity, registration, current-user data, and
the JWT lifecycle.

## When not to use it

Do not add social login, organization roles, or vendor-specific identity flows
to the base project.

## Responsibilities and invariants

- Email is normalized, unique, and is the login identifier.
- Passwords pass Django's configured validators and are never returned.
- Registration creates the user and its account in one transaction.
- Refresh tokens rotate and old tokens are blacklisted by settings; logout
  explicitly blacklists the submitted refresh token.

## Complete canonical artifact

<!-- artifact: src/apps/authentication/__init__.py; profiles: base,full -->
```python
"""Email identity and JWT endpoints."""
```

## Alternatives and trade-offs

Cookie-bound sessions are a strong choice for same-origin browser applications.
Bearer JWTs fit independently deployed API clients but require careful storage,
rotation, revocation, and short access-token lifetimes.

## Required tests

Cover normalization, duplicate registration, password validation, login,
rotation, revocation, logout, and unauthenticated access.

## Related standards

- [User model](models.md)
- [JWT endpoints](urls.md)
- [Account provisioning](services.md)
