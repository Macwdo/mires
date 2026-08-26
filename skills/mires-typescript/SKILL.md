---
name: mires-typescript
description: Apply Macwdo's TypeScript standards for type ownership, shared contracts, API response typing, runtime validation, and module boundaries across frontend and Node codebases.
---

# Mires TypeScript

Find the real contract source before defining a type. Existing OpenAPI code generation, schemas, shared packages, or runtime validators outrank hand-written duplicates.

## Snippet-Driven Implementation

Always start generated TypeScript from the closest snippet in this `SKILL.md`: owned domain type, wire contract, discriminated result, exhaustive branch, runtime parser, or typed API client.

- Preserve the snippet's ownership, narrow exports, explicit wire shape, and exhaustive handling.
- Adapt naming, schema library, generated-client conventions, and error model to the repository.
- Derive from an existing schema or generated type instead of recreating the snippet when the contract already has a source of truth.
- Do not create global type buckets or duplicate backend contracts.
- Use `$mires-react` and `$mires-next` snippets for framework-specific consumers.

Use `$mires-react` for React component and state decisions, `$mires-next` for Next.js boundaries, and `$mires-python` for the Python side of an API contract.

## TypeScript

TypeScript guidance for frontend contracts, API typing, and keeping type ownership aligned with local conventions.

### When To Use

Use for TypeScript type ownership, shared contracts, API response typing, and frontend module boundaries.

### Core Rules

- Prefer types that derive from the real contract source when the repo already has one.
- Keep shared types close to the boundary that owns them.
- Match the existing naming and module layout.

### Preferred Patterns

- Schema-first or contract-first typing when the repo supports it.
- Narrow types near the consumer when global sharing is unnecessary.
- Simple exported types with clear ownership.

### Anti-Patterns

- Duplicated contract definitions across the frontend.
- Global type dumping grounds.
- Type indirection that hides the real data shape.

### Checklist

- Confirm where types are currently owned.
- Reuse the repo's existing schema or contract flow.
- Validate the changed API and UI boundary together.

---

### Contracts And API Integration

- Prefer the repository's existing contract source, schema, or response typing pattern.
- Keep shared types close to the boundary that owns them.
- Avoid duplicating the same payload shape across unrelated modules.

### Owned Contract Reference

Keep wire contracts explicit and colocated with the boundary that owns them:

```ts
export type CustomerSummary = {
  id: string
  name: string
  status: "active" | "inactive"
}

export type CustomerListResponse = {
  items: CustomerSummary[]
  nextCursor: string | null
}
```

If OpenAPI, a generated client, or a runtime schema already owns these types, import or derive them instead.

### Discriminated Result Reference

Represent mutually exclusive outcomes as a union instead of optional fields:

```ts
type SaveResult<T> =
  | { status: "success"; data: T }
  | { status: "validation-error"; fields: Record<string, string> }
  | { status: "error"; message: string }

export function resultMessage<T>(result: SaveResult<T>): string {
  switch (result.status) {
    case "success":
      return "Saved"
    case "validation-error":
      return "Check the highlighted fields"
    case "error":
      return result.message
  }
}
```

Prefer exhaustive branches; do not weaken the union into a bag of nullable properties.

### Runtime Parser Boundary

Inject the repository's schema implementation while keeping the client generic:

```ts
type Parser<T> = {
  parse(value: unknown): T
}

export async function getJson<T>(url: string, parser: Parser<T>): Promise<T> {
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`)
  }

  return parser.parse(await response.json())
}
```

At call sites, pass the existing Zod, Valibot, ArkType, generated, or custom parser rather than hardcoding a new schema library.

### Configuration Reference

Use `satisfies` to validate a configuration shape without unnecessarily widening its inferred values:

```ts
type FeatureConfig = Record<string, { enabled: boolean; rollout: number }>

export const features = {
  billing: { enabled: true, rollout: 100 },
  reports: { enabled: false, rollout: 0 },
} satisfies FeatureConfig
```
