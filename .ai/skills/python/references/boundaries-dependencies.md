---
name: boundaries-dependencies
description: "Mires Python boundary and dependency-injection guidance. Use when separating core logic from I/O, external clients, framework adapters, environment access, and global construction."
---

# Python Boundaries Dependencies

Use this skill when code touches external services, repositories, clients, framework adapters, or environment configuration.

## Rules

- Pass external clients, repositories, and configurable collaborators into functions instead of constructing them deep inside business logic.
- Keep I/O, network calls, filesystem access, framework adapters, and environment reads at module boundaries.
- Keep core logic testable without booting a framework or patching module globals.
- Use dependency functions at the edge when callers need SDK clients or app settings.
- Prefer explicit collaborators over implicit singletons.

## Example

```python
from collections.abc import Callable


def build_invoice_message(
    *,
    customer_name: str,
    total_cents: int,
    format_currency: Callable[[int], str],
) -> str:
    return f"{customer_name}: {format_currency(total_cents)}"
```
