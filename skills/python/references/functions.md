---
name: functions
description: "Mires function-first Python implementation guidance. Use for plain modules, services, transformations, orchestration helpers, and utilities where small typed functions should be preferred over unnecessary classes."
---

# Python Functions

Use this skill when deciding whether Python code should be a function, class, service helper, or utility module.

## Rules

- Read the target file, sibling modules, and nearby tests before introducing a new shape.
- Prefer plain functions for services, transformations, orchestration helpers, command helpers, and utilities.
- Introduce a class only when the code needs durable state, a protocol boundary, or a cohesive object lifecycle.
- Keep framework glue thin and keep plain Python in the middle of the implementation.
- Keep public entry points easy to grep and helpers close to the code that uses them.

## Workflow

1. Match the repo naming and import style.
2. Write the smallest useful public function first.
3. Extract helpers only after the main responsibility is obvious.
