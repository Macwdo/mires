---
name: state-mutation
description: "Mires Python state and mutation guidance. Use when deciding whether functions should return new values, mutate inputs, update shared state, or expose side effects explicitly."
---

# Python State Mutation

Use this skill when refactoring functions that update state, shared objects, caches, or mutable inputs.

## Rules

- Prefer returning new values over mutating shared state in place.
- If a function updates state, make the side effect explicit in the function name and signature.
- Avoid hidden global caches, mutable singletons, and mutable default arguments in normal application code.
- Keep transaction-like state changes close to their boundary so tests can assert observable effects.
- Document only non-obvious side effects; do not comment obvious assignments.
