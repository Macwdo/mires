# Application reference tree

This directory mirrors the application layer of the base project. Each child
package owns one cohesive concern and may depend only on packages below it in
the following direction:

`common` → `authentication` → `account` → `api` and `customer`.

The empty package artifact makes `apps` importable without adding runtime
behavior.

<!-- artifact: src/apps/__init__.py; profiles: base,full -->
```python
"""Project application packages."""
```

## Related standards

- [Common foundations](common/README.md)
- [API boundary](api/README.md)
- [Customer example](customer/README.md)
