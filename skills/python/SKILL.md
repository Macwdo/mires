---
name: python
description: Generic Python module, typing, boundary, error, and test guidance for backend code.
---

# Python

## When To Use

Use for generic Python implementation decisions that are not framework-specific.

## Core Rules

- Prefer small typed functions unless the repo clearly favors another shape.
- Keep I/O boundaries explicit.
- Match nearby naming, imports, and helper placement.
- Reuse the existing testing and validation workflow.

## Preferred Patterns

- Explicit function signatures.
- Visible dependency injection.
- Focused modules with clear ownership.
- Behavior-first tests.

## Anti-Patterns

- Hidden global state.
- Implicit side effects.
- Oversized modules with mixed concerns.
- Unchecked assumptions about typing or mutation.

## Checklist

- Confirm the existing module shape.
- Confirm the current typing and validation style.
- Reuse existing test helpers and workflows.
- Keep changes local to the touched behavior.

## References Index

- `references/functions.md`
- `references/typing-signatures.md`
- `references/boundaries-dependencies.md`
- `references/module-shape.md`
- `references/state-mutation.md`
- `references/errors.md`
- `references/devex-patterns.md`
- `references/tests-helpers.md`
- `references/tests-workflow.md`
- `references/validation.md`
