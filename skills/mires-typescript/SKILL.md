---
name: mires-typescript
description: Apply Macwdo's TypeScript standards for type ownership, shared contracts, and API response typing across frontend and Node codebases. Use when deciding where types live, integrating a typed API client, or reviewing contract drift between backend and frontend.
---

# Mires TypeScript

Use this skill for TypeScript type ownership and contract decisions, independent of any UI framework. Inspect the target repository first: an existing schema or codegen pipeline outranks everything here.

## Start With The Contract

1. Find where the contract already lives: an OpenAPI schema, a codegen output, a shared package, or hand-written types.
2. Follow that source. Do not add a second definition of the same contract.
3. Place new types next to the boundary that owns them, not in a global type bucket.
4. Validate the API and its consumer together when a contract changes.

## Decision Rules

- Derive types from the real contract source when the repository has one.
- Keep a type narrow and local until a second consumer actually needs it.
- Prefer an explicit exported type over inference that hides the wire shape.
- Never duplicate a contract definition across the frontend.

Read `references/typescript/rules.md` for the full rules, anti-patterns, and checklist. Read `references/typescript/contracts-and-api-integration.md` for the API integration and contract-ownership patterns.

For React and Next.js component, state, and data-fetching decisions, use `$mires-react`. For the Python side of the same contract, use `$mires-python`.

## References

- `references/typescript/rules.md`: type ownership, contract, and module-boundary rules
- `references/typescript/contracts-and-api-integration.md`: contract-first typing and API integration patterns
