---
name: anti-patterns
description: "Mires React anti-pattern guidance. Use to avoid caching API responses in Zustand, React Query for local state, manual duplicated zod types, broad stores, and unnecessary form tooling."
---

# React Anti Patterns

Use this skill as a negative checklist for React and Next.js feature code.

## Rules

- Do not cache API response bodies in Zustand.
- Do not mirror React Query results into Zustand unless there is a narrowly justified integration boundary.
- Do not use React Query for purely local UI state.
- Do not wrap a trivial single search input in `react-hook-form`.
- Do not create a `zod` schema and then manually duplicate its type definitions unless a library boundary makes that unavoidable.
- Do not create broad stores when a narrow selector-based Zustand store will do.
- Add `"use client"` only where forms, query providers, Zustand consumers, or interactive UI require it.
