# Account tenancy

## Purpose and when to use it

Use this package for the base project's deliberately simple tenancy model:
every user owns exactly one account and every tenant record references it.

## When not to use it

Do not use this model when users can join multiple accounts. Adopt the
multi-account recipe and make account selection explicit instead.

## Responsibilities and invariants

- `Account.user` is one-to-one and cannot be null.
- Inactive accounts cannot access account-owned endpoints.
- Every account-owned lookup scopes by account before object lookup.

## Complete canonical artifact

<!-- artifact: src/apps/account/__init__.py; profiles: base,full -->
```python
"""Single-account tenancy primitives."""
```

## Alternatives and trade-offs

One account per user removes ambiguous request context. It does not model teams,
invitations, or role-bearing memberships.

## Required tests

Registration must create one account; tenant tests must prove cross-account
reads, updates, and deletes return not-found.

## Related standards

- [Account models](models.md)
- [Customer isolation](../customer/README.md)
