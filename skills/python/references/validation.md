---
name: validation
description: "Mires Python validation guidance. Use for choosing focused pytest, Ruff, format, type-check, and project-specific commands after Python changes."
---

# Python Validation

Use this skill before finishing Python implementation work.

## Rules

- Run the smallest validation that proves the change works.
- Prefer a focused `pytest` target, a single module test run, or the narrowest lint/type check that covers the edit.
- If the repo uses Ruff, MyPy, Pyright, pytest, or project-specific make targets, reuse them.
- If typing matters for the change, run the relevant type checker on the touched scope.
- If formatting matters, run the repo formatter instead of hand-formatting around it.
- Do not claim confidence without running at least one relevant check when a check is available.
