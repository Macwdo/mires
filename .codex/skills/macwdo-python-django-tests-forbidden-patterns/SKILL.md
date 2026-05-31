---
name: macwdo-python-django-tests-forbidden-patterns
description: "Macwdo Django forbidden test-pattern guidance. Use to avoid factory_boy, model factories, Django fixture files, hardcoded URLs, opaque fixtures, and missing response-body assertions."
---

# Django Tests Forbidden Patterns

Use this skill as a negative checklist for Django tests.

## Rules

- Do not use `factory_boy`.
- Do not use model factories of any kind.
- Do not use Django fixture files such as `.json`, `.yaml`, or `.xml`.
- Do not hardcode URLs.
- Do not skip response-body assertions on API tests.
- Do not hide important setup inside opaque fixtures when a helper would make the flow clearer.
- If a factory seems convenient, create a helper instead.
