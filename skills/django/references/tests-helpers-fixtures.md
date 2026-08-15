---
name: tests-helpers-fixtures
description: "Mires Django helper and fixture guidance. Use for helper-first setup, keyword-only test helpers, sensible defaults, fixtures wrapping helpers, and visible API-driven state creation."
---

# Django Tests Helpers Fixtures

Use this skill when setting up reusable Django test state.

## Rules

- Build state through helpers or the public API whenever practical.
- Helpers should use keyword-only arguments and sensible defaults.
- If setup is missing, add or extend `tests/helpers.py` instead of creating one-off ORM setup inline.
- Fixtures should wrap helpers, authenticated clients, or other common setup utilities.
- Fixtures should not replace helpers with hidden ORM-heavy setup.
- Expected shared fixtures often include `api_client`, `common_user`, and `api_client_with_common_user`.
