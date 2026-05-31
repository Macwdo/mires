---
name: macwdo-python-django-tests-naming-structure
description: "Macwdo Django test naming and file-structure guidance. Use for src/apps/<app>/tests layout, helpers.py, conftest.py, one-line docstrings, and test_resource_action_condition_expected_result names."
---

# Django Tests Naming Structure

Use this skill when creating or reorganizing Django tests.

## Rules

- Use `src/apps/<app>/tests/` with `__init__.py`, `helpers.py`, and `test_<feature>.py` when the repo follows that layout.
- Name tests with `test_<resource>_<action>_<condition>_<expected_result>`.
- Give every test a one-line docstring describing the behavior under test.
- Keep route names and helper imports consistent with nearby tests.
- Use app-level `conftest.py` only for fixtures that are genuinely shared.

## Examples

- `test_register_returns_201_when_valid_data`
- `test_register_returns_400_when_email_already_exists`
- `test_me_returns_401_when_not_authenticated`
