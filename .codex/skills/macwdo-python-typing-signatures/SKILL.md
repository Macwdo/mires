---
name: macwdo-python-typing-signatures
description: "Macwdo Python typing and signature guidance. Use for explicit public signatures, keyword-only service arguments, concrete collection types, TypedDict, dataclass, and small domain types."
---

# Python Typing Signatures

Use this skill when adding or refactoring typed Python APIs.

## Rules

- Add type hints to public functions, methods, return values, and important local data structures.
- Prefer concrete types such as `list[str]`, `dict[str, Any]`, `Path`, and domain-specific aliases over vague placeholders.
- Use keyword-only arguments for service-style functions, helpers, and orchestration entry points when clarity improves.
- Use `TypedDict`, `dataclass`, or small domain types when dictionaries become ambiguous.
- Keep types aligned with the repo type checker and Python version.

## Example

```python
from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class ReportSummary(TypedDict):
    path: Path
    line_count: int


def summarize_report(*, path: Path) -> ReportSummary:
    line_count = len(path.read_text().splitlines())
    return {"path": path, "line_count": line_count}
```
