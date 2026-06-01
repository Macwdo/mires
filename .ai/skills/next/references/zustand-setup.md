---
name: zustand-setup
description: "Mires Next.js Zustand setup guidance. Use for a small src/stores example store, client-only shared state, selector-friendly stores, and keeping server data in React Query."
---

# Next Zustand Setup

Use this skill when adding baseline Zustand wiring to a Next.js app.

## Rules

- Create one small example store in `src/stores/` when starter wiring is requested.
- Use Zustand for local client state only.
- Do not use Zustand as a replacement for server data that belongs in React Query.
- Keep stores focused and easy to select from.
- Consume stores only from client components.
