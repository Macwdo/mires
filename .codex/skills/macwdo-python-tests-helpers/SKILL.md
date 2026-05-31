---
name: macwdo-python-tests-helpers
description: "Macwdo Python test helper guidance. Use for visible setup, explicit fixtures, helper functions, monkeypatching, and mocking only true external boundaries."
---

# Python Tests Helpers

Use this skill when test setup repeats or needs fixtures, helpers, or mocks.

## Rules

- Prefer small helpers and explicit fixtures over hidden setup chains.
- Keep data construction close to the test unless it is genuinely repeated.
- Mock only the true external boundary, not the logic under test.
- Use keyword-only arguments in reusable helpers when setup needs variation.
- Keep monkeypatching and patching near the test that needs it.
