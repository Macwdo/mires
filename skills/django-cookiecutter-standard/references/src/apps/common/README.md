# Common application foundations

## Purpose and when to use it

Use this package for small, dependency-free primitives shared by multiple
domain applications.

## When not to use it

Do not place business workflows, tenant policy, or vendor integrations here.

## Responsibilities and invariants

- Shared models remain abstract.
- Exceptions expose stable machine codes and safe public messages.
- The package imports no domain application.

## Complete canonical artifact

<!-- artifact: src/apps/common/__init__.py; profiles: base,full -->
```python
"""Dependency-free application primitives."""
```

## Alternatives and trade-offs

Keeping primitives in their first owning application reduces indirection. Move
code here only after at least two applications genuinely share it.

## Required tests

Concrete models inheriting the timestamp base are exercised by their owning
application tests.

## Related standards

- [Shared models](models.md)
- [Public exceptions](exceptions.md)
