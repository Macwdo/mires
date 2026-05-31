---
name: macwdo-typescript-next-react-query-setup
description: "Macwdo Next.js React Query setup guidance. Use for QueryClient provider components, app-root mounting, retry/staleTime defaults, axios query functions, and client provider boundaries."
---

# Next React Query Setup

Use this skill when adding baseline React Query wiring to a Next.js app.

## Rules

- Create a shared `QueryClient` provider component for client-side usage.
- Mount it once near the app root.
- Use a small default config; prefer `retry: 1` and a non-zero `staleTime`.
- Use axios inside query functions by default unless the user asks for `fetch`.
- Keep provider code in a client component and keep server components server-first outside that boundary.
