---
name: mires-next
description: Apply Macwdo's Next.js App Router standards for routing, Server and Client Component boundaries, data fetching, caching, forms, mutations, API integration, security, and deployment. Use when Next.js owns the application or page boundary.
---

# Mires Next

Use this skill with `$mires-react`. Prefer server-first composition, thin route files, and explicit ownership of server data, URL state, form state, and local UI state. Inspect the repository's router, rendering mode, data layer, component primitives, and deployment constraints before editing.

## Snippet-Driven Implementation

Always begin Next.js code generation from the closest snippet in this `SKILL.md`: Server Component, Client Component leaf, server-only data function, Route Handler, Server Action, cache invalidation, or browser test.

- Preserve server/client ownership, serializable boundaries, validation, authorization, cache behavior, and explicit outcomes shown by the snippet.
- Adapt aliases, validators, authentication helpers, data services, runtime, and cache model to the installed Next.js version and repository conventions.
- Do not add a Server Action, Route Handler, or client data library when the repository already owns the boundary differently.
- Use `$mires-react` snippets for component and interaction details and `$mires-typescript` snippets for contracts.
- Generated code must be recognizably based on the closest snippet, with deviations justified by repository evidence.

## Companion Routing

- Apply `$mires-react` for component composition, forms, accessibility, and client state.
- Apply `$mires-typescript` for API contracts and shared type ownership.

Do not move an entire feature to the client because one leaf is interactive. Keep `"use client"` at the smallest practical boundary and make pending, empty, error, retry, and mutation outcomes explicit.

## App Router Organization

- Keep `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`, and route handlers thin.
- Put product behavior in feature modules and reusable visual primitives in the established component layer.
- Use route groups and nested layouts to express navigation and ownership, not as arbitrary folders.
- Keep dynamic segment parsing and authorization close to the server boundary.
- Generate metadata on the server and avoid fetching the same resource independently for metadata and content when the framework can reuse it.

## Server And Client Boundaries

- Fetch protected data in Server Components or server-side services when interactivity does not require browser ownership.
- Pass serializable data through the boundary; do not pass database models, clients, class instances, or secrets to Client Components.
- Make the smallest interactive leaf a Client Component.
- Use server actions only when the repository already adopts them and their deployment/runtime constraints are understood.
- Keep providers narrow and mount them only around the client subtree that needs them.

## Fetching, Caching, And Revalidation

- Determine whether data is static, request-scoped, user-scoped, or frequently changing before choosing cache behavior.
- Never cache one user's protected data across users.
- Use explicit cache tags or paths when a mutation must invalidate server-rendered data.
- Keep client query keys stable and derived from every input that changes the result.
- Avoid maintaining competing server and client caches for the same ownership boundary without a clear synchronization rule.
- Make pagination, filters, sorting, and search part of the URL when they define a shareable view.

## Mutations And Forms

- Validate untrusted inputs at the server boundary even when the client already validates them.
- Return typed field and form errors instead of parsing exception strings in the UI.
- Make pending and double-submit behavior explicit.
- Revalidate or update the owning cache after success; do not rely on a full-page reload as an implicit consistency strategy.
- Preserve user input after recoverable failures and move focus to meaningful error feedback.

## Route Handlers And BFF Boundaries

- Use route handlers as transport adapters, not a second domain layer.
- Keep authentication, CSRF/origin checks, cookies, headers, and upstream error translation explicit.
- Forward only required headers and never reflect arbitrary client headers upstream.
- Normalize upstream error bodies before returning them to the browser.
- Compare origin and host against the public forwarded protocol and host when running behind a proxy.

## Environment And Security

- Treat only `NEXT_PUBLIC_*` values as intentionally browser-visible.
- Read secrets in server-only modules and prevent accidental client imports.
- Enforce authorization in the server/data boundary for every protected read and mutation.
- Validate redirects and callback URLs against an allowlist.
- Set cookies with intentional `HttpOnly`, `Secure`, `SameSite`, path, and lifetime values.
- Use the repository's CSP and image/domain configuration instead of broad wildcards.

## Operations And Performance

- Keep Node and Edge runtime choices explicit; do not import Node-only libraries into Edge code.
- Verify standalone/container output, health checks, environment injection, and proxy behavior against the deployment target.
- Use image and font optimization without causing layout shift.
- Stream meaningful server boundaries with intentional loading fallbacks.
- Inspect bundle impact before adding client libraries or moving code across the server boundary.
- Report provider-dependent or deployment-only checks that could not run locally.

## Testing

- Unit-test server services and validation independently from Next.js rendering.
- Test route handlers as HTTP boundaries with authentication and error translation.
- Test Server Components at the repository's supported level; do not invent unsupported infrastructure.
- Use browser tests for navigation, URL state, responsive layouts, hydration, focus, cookies, and full mutation flows.
- Verify production build behavior when changing routing, runtime, configuration, environment variables, or server/client boundaries.

### Server Component With A Client Leaf

Fetch on the server and pass a small serializable contract to the interactive leaf:

```tsx
// app/customers/page.tsx
import { CustomerFilter } from "./customer-filter"
import { listCustomers } from "@/features/customers/server/list-customers"

export default async function CustomersPage() {
  const customers = await listCustomers()

  return <CustomerFilter customers={customers} />
}

// app/customers/customer-filter.tsx
"use client"

import { useMemo, useState } from "react"

type Customer = { id: string; name: string }

export function CustomerFilter({ customers }: { customers: Customer[] }) {
  const [query, setQuery] = useState("")
  const visible = useMemo(
    () => customers.filter((customer) => customer.name.includes(query)),
    [customers, query],
  )

  return (
    <section>
      <label htmlFor="customer-search">Search customers</label>
      <input id="customer-search" value={query} onChange={(event) => setQuery(event.target.value)} />
      <ul>{visible.map((customer) => <li key={customer.id}>{customer.name}</li>)}</ul>
    </section>
  )
}
```

If the dataset is large or shareable filtering matters, move the query to URL/server ownership instead of shipping every row to the client.

### Server-Only Data Function

Keep credentials and upstream translation outside route components:

```ts
import "server-only"

import { parseCustomerList } from "@/features/customers/contracts"

export type CustomerSummary = {
  id: string
  name: string
}

export async function listCustomers(): Promise<CustomerSummary[]> {
  const apiUrl = process.env.API_URL
  const apiToken = process.env.API_TOKEN

  if (!apiUrl || !apiToken) {
    throw new Error("Customer API configuration is missing")
  }

  const response = await fetch(`${apiUrl}/customers`, {
    headers: { Authorization: `Bearer ${apiToken}` },
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error(`Customer API failed with ${response.status}`)
  }

  return parseCustomerList(await response.json())
}
```

Implement `parseCustomerList` with the repository's existing runtime schema or generated contract.

### Route Handler Reference

Keep the handler as an HTTP adapter around validation and a service:

```ts
import { createCustomer } from "@/features/customers/server/create-customer"
import { customerInputSchema } from "@/features/customers/contracts"

export async function POST(request: Request): Promise<Response> {
  const input = customerInputSchema.parse(await request.json())
  const customer = await createCustomer(input)

  return Response.json(customer, { status: 201 })
}
```

Add authentication, authorization, CSRF/origin validation, and domain-error translation through the project's established helpers.

### Server Action And Revalidation Reference

Use this only when the repository already uses Server Actions:

```ts
"use server"

import { revalidatePath } from "next/cache"
import { createCustomer } from "@/features/customers/server/create-customer"
import { customerFormSchema } from "@/features/customers/contracts"

export async function createCustomerAction(formData: FormData) {
  const input = customerFormSchema.parse(Object.fromEntries(formData))
  await createCustomer(input)
  revalidatePath("/customers")

  return { ok: true } as const
}
```

Prefer tag-based invalidation when the repository's cache model already tags the underlying resource.

### Browser Test Reference

```ts
import { expect, test } from "@playwright/test"

test("filters customers without losing keyboard focus", async ({ page }) => {
  await page.goto("/customers")

  const search = page.getByLabel("Search customers")
  await search.fill("Ada")

  await expect(page.getByRole("listitem")).toHaveText(["Ada Lovelace"])
  await expect(search).toBeFocused()
})
```

## Next.js

Next.js patterns for server-first routing, App Router boundaries, project setup, and supporting client integrations.

### When To Use

Use for Next.js routing, server and client component boundaries, project setup, and Next-specific supporting patterns.

### Core Rules

- Inspect the current app structure and routing pattern first.
- Prefer server-first boundaries when they match the repo.
- Keep supporting setup aligned with the existing stack.

### Preferred Patterns

- Clear server and client ownership.
- App Router conventions that match nearby files.
- Minimal setup changes scoped to the touched boundary.

### Anti-Patterns

- Broad client-only rewrites without need.
- New routing or state abstractions that do not match the repo.
- Pulling in unrelated setup changes for a small feature.

### Checklist

- Confirm the app or pages router in use.
- Confirm the current server/client split.
- Read the complete Next.js topic, then apply only the sections relevant to the change.

---

### Next Server First

Use this section when implementing features in a Next.js App Router project.

#### Rules

- Prefer App Router and TypeScript defaults from the project template.
- Keep components server-first.
- Add `"use client"` only where forms, query providers, Zustand consumers, or interactive UI require it.
- Keep client providers as narrow as practical while still covering client hooks that need them.
- Use the project alias already generated by the template instead of rewriting imports to relative paths without a reason.

---

### Next Project Bootstrap

Use this section when the user wants a fresh Next.js codebase with the preferred frontend stack.

#### Rules

- Package manager: `pnpm`.
- Bootstrap through `pnpm dlx shadcn@latest init` instead of manually assembling `package.json`.
- Install runtime packages with `pnpm add`; do not edit dependencies by hand.
- Default stack: shadcn/ui, axios, React Hook Form, Zod, `@hookform/resolvers`, TanStack React Query, and Zustand.
- Do not add auth, persistence, state machines, or testing tools unless the user asks.

#### Workflow

1. Derive the app name from the request.
2. Run `pnpm dlx shadcn@latest init --name <app-name> --template next --defaults`.
3. Enter the new project directory.
4. Run `pnpm add axios react-hook-form zod @hookform/resolvers @tanstack/react-query zustand`.
5. Add only the minimum starter wiring requested by the task.

---

### Next React Query Setup

Use this section when adding baseline React Query wiring to a Next.js app.

#### Rules

- Create a shared `QueryClient` provider component for client-side usage.
- Mount it once near the app root.
- Use a small default config; prefer `retry: 1` and a non-zero `staleTime`.
- Use axios inside query functions by default unless the user asks for `fetch`.
- Keep provider code in a client component and keep server components server-first outside that boundary.

---

### Next Axios Setup

Use this section when adding HTTP client wiring to a Next.js app.

#### Rules

- Create a shared axios instance in a small `lib` module such as `src/lib/axios.ts`.
- Centralize base configuration there so React Query hooks import the same client.
- Keep the instance simple by default.
- Do not invent interceptors, auth headers, or environment handling unless the task requires them.
- Do not create multiple competing API clients.

---

### Next Zustand Setup

Use this section when adding baseline Zustand wiring to a Next.js app.

#### Rules

- Create one small example store in `src/stores/` when starter wiring is requested.
- Use Zustand for local client state only.
- Do not use Zustand as a replacement for server data that belongs in React Query.
- Keep stores focused and easy to select from.
- Consume stores only from client components.

---

### Next Form Setup

Use this section when starter output or a feature needs a validated client form in Next.js.

#### Rules

- Create the form in a client component.
- Define the schema with Zod first, then infer the form type from that schema.
- Use `react-hook-form` and `zodResolver` for multi-field validation.
- Use shadcn form primitives and inputs when the project uses shadcn UI.
- Do not add a demo form if the user only asked for project bootstrap and no starter wiring.
