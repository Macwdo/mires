---
name: next
description: Next.js patterns for server-first routing, App Router boundaries, project setup, and supporting client integrations.
---

# Next.js

## When To Use

Use for Next.js routing, server and client component boundaries, project setup, and Next-specific supporting patterns.

## Core Rules

- Inspect the current app structure and routing pattern first.
- Prefer server-first boundaries when they match the repo.
- Keep supporting setup aligned with the existing stack.

## Preferred Patterns

- Clear server and client ownership.
- App Router conventions that match nearby files.
- Minimal setup changes scoped to the touched boundary.

## Anti-Patterns

- Broad client-only rewrites without need.
- New routing or state abstractions that do not match the repo.
- Pulling in unrelated setup changes for a small feature.

## Checklist

- Confirm the app or pages router in use.
- Confirm the current server/client split.
- Load only the Next.js references relevant to the change.

## References Index

- `references/explorer.md`
- `references/server-first.md`
- `references/project-bootstrap.md`
- `references/react-query-setup.md`
- `references/axios-setup.md`
- `references/zustand-setup.md`
- `references/form-setup.md`
