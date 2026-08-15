---
name: typescript
description: TypeScript guidance for frontend contracts, API typing, and keeping type ownership aligned with local conventions.
---

# TypeScript

## When To Use

Use for TypeScript type ownership, shared contracts, API response typing, and frontend module boundaries.

## Core Rules

- Prefer types that derive from the real contract source when the repo already has one.
- Keep shared types close to the boundary that owns them.
- Match the existing naming and module layout.

## Preferred Patterns

- Schema-first or contract-first typing when the repo supports it.
- Narrow types near the consumer when global sharing is unnecessary.
- Simple exported types with clear ownership.

## Anti-Patterns

- Duplicated contract definitions across the frontend.
- Global type dumping grounds.
- Type indirection that hides the real data shape.

## Checklist

- Confirm where types are currently owned.
- Reuse the repo's existing schema or contract flow.
- Validate the changed API and UI boundary together.

## References Index

- `references/contracts-and-api-integration.md`
