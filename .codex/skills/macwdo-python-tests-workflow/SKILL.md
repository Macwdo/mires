---
name: macwdo-python-tests-workflow
description: "Macwdo Python testing workflow guidance. Use for behavior-first pytest tests, reading the existing suite, narrow red-green-refactor loops, and focused validation commands."
---

# Python Tests Workflow

Use this skill when adding or changing Python tests outside a framework-specific flow.

## Rules

- Inspect the current test suite before adding new tests.
- Default to `pytest` when the repo has no stronger convention.
- Write tests around user-visible or caller-visible contracts first.
- Assert return values, raised exceptions, and observable side effects.
- Name tests so the condition and expected outcome are obvious.

## Workflow

1. Start from the behavior.
2. Make the smallest production change that satisfies it.
3. Run the narrowest command that proves the behavior.
