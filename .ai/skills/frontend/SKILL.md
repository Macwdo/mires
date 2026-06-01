---
name: frontend
description: Cross-cutting frontend rules for UI ownership, API integration, and keeping React or Next.js changes aligned with local conventions.
---

# Frontend

## When To Use

Use for frontend work that spans routing, UI ownership, state boundaries, API integration, or multiple frontend libraries.

## Core Rules

- Inspect the app structure and existing UI patterns first.
- Keep ownership of data, form state, and UI state explicit.
- Prefer local conventions over generic component abstractions.

## Preferred Patterns

- Clear separation between server data, client UI state, and form state.
- API integration patterns that match nearby code.
- Intentional component boundaries.

## Anti-Patterns

- One-off state models that fight the rest of the app.
- New UI abstractions without local precedent.
- Mixing API, form, and display concerns into one oversized component.

## Checklist

- Identify the routing and component boundary first.
- Confirm where server data and client state already live.
- Load only the React, Next.js, or TypeScript references you need.

## References Index

- `references/ui-ownership.md`
