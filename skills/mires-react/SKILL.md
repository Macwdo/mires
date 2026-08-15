---
name: mires-react
description: Apply Macwdo's opinionated React and Next.js standards from an executable Markdown handbook. Use for App Router architecture, component design, server and client boundaries, forms, API contracts, data fetching, accessibility, security, performance, operations, or reconstructing a reference application.
---

# Mires React

Use this optional Mires companion after inspecting the target repository. Existing project conventions take precedence; use the bundled handbook to fill genuine gaps, implement new surfaces, or review decisions.

## Start With The Task

1. Read `references/handbook/docs/architecture.md` and `references/handbook/docs/conventions.md` for cross-cutting design work.
2. Read only the documents, recipes, and canonical artifacts relevant to the requested surface.
3. Inspect routing, server and client boundaries, component composition, state ownership, validation, accessibility, and tests in the target repository before editing.
4. Adapt the reference instead of copying application-specific assumptions.
5. Run the target repository's checks; reconstruct a handbook profile only when validating the reference itself.

## Route By Surface

Start from the condensed rules, then go to the handbook when you need the full design rationale or a canonical artifact.

- Cross-cutting UI ownership and state boundaries: `references/frontend/rules.md`
- React component, state, and form rules: `references/react/rules.md`, routed by `references/react/explorer.md`
- Next.js App Router, bootstrap, and library setup rules: `references/next/rules.md`, routed by `references/next/explorer.md`

- Component boundaries and composition: `references/handbook/docs/component-design.md`
- API input and output contracts: `references/handbook/docs/api-contracts.md`
- Forms and mutation outcomes: `references/handbook/docs/forms.md`
- Fetching, caching, filters, pagination, and mutations: `references/handbook/docs/data-fetching.md`
- Accessibility: `references/handbook/docs/accessibility.md`
- Security and environment boundaries: `references/handbook/docs/security.md`
- Performance: `references/handbook/docs/performance.md`
- Deployment and operational behavior: `references/handbook/docs/operations.md`
- Optional product capabilities: load only the relevant file under `references/handbook/recipes/`.
- Exact dependency snapshot: `references/handbook/docs/version-snapshot.md`
- Disposable reference generation: `references/handbook/docs/reconstruction.md`

## Preserve The Handbook Contract

- Treat the bundled Markdown as reference source, not as code to paste blindly.
- Do not commit reconstructed output.
- Prefer Server Components and keep `"use client"` at the smallest interactive boundary.
- Keep route files thin and product behavior in feature modules.
- Separate server data, form state, URL state, and local UI state.
- Validate external input and API output at runtime.
- Make pending, empty, error, retry, and mutation outcomes explicit.
- Do not add global state or abstraction layers without demonstrated need.

## Source

Read `references/source.md` for provenance. This is a standards handbook with reconstructable examples, not a product template or generator.

For type ownership and API contract decisions, use `$mires-typescript`.
