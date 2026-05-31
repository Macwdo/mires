---
name: macwdo-python-errors
description: "Macwdo Python error-handling guidance. Use for explicit exceptions, readable messages, translating low-level failures at boundaries, and avoiding swallowed errors."
---

# Python Errors

Use this skill when adding or reviewing exception behavior in Python modules and services.

## Rules

- Raise explicit exceptions with human-readable messages.
- Do not swallow exceptions just to keep control flow moving.
- Translate low-level exceptions at boundaries when the caller needs a more useful domain error.
- Keep retry, logging, and fallback behavior tied to a real operational need.
- Test raised exceptions and failure-side effects when they are part of the caller-visible contract.
