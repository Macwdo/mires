---
name: mires-react
description: Apply Macwdo's React standards for component ownership, composition, forms, server and client state, accessibility, performance, and testing. Use for React UI work that is not primarily a Next.js routing or server-boundary decision.
---

# Mires React

Build React surfaces with explicit ownership and the smallest necessary client state. Inspect existing components, primitives, data hooks, form conventions, accessibility patterns, and tests before editing.

## Snippet-Driven Implementation

Always start generated React code from the closest snippet in this `SKILL.md`: component composition, local state, reducer, server state, client store, form, or test. Use `$mires-next` snippets as well when Next.js owns the rendering or routing boundary.

- Preserve explicit props, state ownership, accessible semantics, typed events, and visible async states.
- Adapt primitives, styling, form libraries, query keys, stores, and test helpers to the repository.
- Do not introduce React Query, Zustand, Zod, or React Hook Form solely because a snippet shows it; use the repository's established equivalent.
- Keep literal breakpoint and primitive ownership constraints when adapting a snippet.
- Generate or update the matching interaction test whenever behavior changes.

## Companion Routing

- Use `$mires-next` in addition to this skill when Next.js App Router, Server Components, route handlers, caching, or deployment behavior is involved.
- Use `$mires-typescript` for shared contract and type-ownership decisions.

Preserve literal UI constraints such as breakpoint ownership, mobile-only behavior, primitive placement, and whether behavior belongs in a row, dialog, drawer, sheet, or page.

## Component Composition

- Give each component one visual or behavioral responsibility.
- Prefer composition, slots, compound components, and explicit variants over boolean-prop matrices.
- Keep domain behavior in feature components and low-level styling in primitives.
- Preserve the primitive that owns focus, dismissal, portal behavior, scrolling, and keyboard interaction.
- Do not hide materially different desktop and mobile layouts behind one component full of breakpoint branches when two small composed surfaces are clearer.

## Accessibility

- Use native elements before recreating semantics with `div` and ARIA.
- Every interactive control must be keyboard reachable and have an accessible name.
- Preserve visible focus; do not remove outlines without an equally clear replacement.
- Associate form errors and descriptions with their fields.
- Use dialogs, sheets, menus, comboboxes, and tooltips through established accessible primitives.
- Announce asynchronous success or failure when the visual update alone is insufficient.
- Respect reduced-motion preferences and avoid motion required to understand state.

## Security

- Treat rendered external text as untrusted and avoid raw HTML insertion.
- Do not place secrets in client bundles, browser storage, or public environment variables.
- Keep authorization on the server; client-side hiding is presentation, not access control.
- Validate redirect targets, external URLs, and uploaded file metadata.
- Avoid persisting sensitive server data in global client stores.

## Performance

- Measure before memoizing; do not add `memo`, `useMemo`, or `useCallback` by reflex.
- Keep state close to the components that consume it to avoid broad rerenders.
- Virtualize only genuinely large lists and preserve keyboard/accessibility behavior.
- Lazy-load expensive optional surfaces, not core content needed for first paint.
- Avoid effects that mirror props or derive state that can be computed during render.

## Testing

- Test behavior through accessible roles, labels, and visible outcomes.
- Prefer user interactions over calling component internals.
- Cover pending, empty, error, retry, success, disabled, and validation states when they exist.
- Reuse the repository's render helpers, providers, factories, and server mocks.
- Use browser tests for focus management, responsive composition, navigation, portals, and cross-component workflows.
- Validate the exact breakpoint and primitive ownership required by the request.

### Component Composition Reference

Use explicit slots instead of boolean props that attempt to represent every layout:

```tsx
import { useId, type ReactNode } from "react"

type UserSummaryProps = {
  actions?: ReactNode
  description: ReactNode
  title: ReactNode
}

export function UserSummary({ actions, description, title }: UserSummaryProps) {
  const titleId = useId()

  return (
    <article aria-labelledby={titleId}>
      <header>
        <h2 id={titleId}>{title}</h2>
        {actions && <div aria-label="User actions">{actions}</div>}
      </header>
      <div>{description}</div>
    </article>
  )
}
```

Keep interactive actions outside the summary's data ownership. Adapt the semantic element and primitive to the surface.

### Local Workflow State Reference

Use a discriminated reducer when transitions matter more than independent fields:

```tsx
import { useReducer } from "react"

type State =
  | { status: "idle" }
  | { status: "submitting" }
  | { status: "success"; message: string }
  | { status: "error"; message: string }

type Action =
  | { type: "submit" }
  | { type: "resolve"; message: string }
  | { type: "reject"; message: string }
  | { type: "reset" }

function reducer(_state: State, action: Action): State {
  switch (action.type) {
    case "submit":
      return { status: "submitting" }
    case "resolve":
      return { status: "success", message: action.message }
    case "reject":
      return { status: "error", message: action.message }
    case "reset":
      return { status: "idle" }
  }
}

export function SaveButton() {
  const [state, dispatch] = useReducer(reducer, { status: "idle" })
  const pending = state.status === "submitting"

  return (
    <button disabled={pending} onClick={() => dispatch({ type: "submit" })}>
      {pending ? "Saving…" : "Save"}
    </button>
  )
}
```

Use component state instead when the state is only a simple toggle or input.

### Interaction Test Reference

Test what the user can observe:

```tsx
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

it("submits once and exposes the pending state", async () => {
  const user = userEvent.setup()
  render(<ProfileForm onSubmit={vi.fn()} />)

  await user.type(screen.getByLabelText("Name"), "Ada")
  await user.click(screen.getByRole("button", { name: "Save" }))

  expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled()
})
```

## Frontend

Cross-cutting frontend rules for UI ownership, API integration, and keeping React or Next.js changes aligned with local conventions.

### When To Use

Use for frontend work that spans routing, UI ownership, state boundaries, API integration, or multiple frontend libraries.

### Core Rules

- Inspect the app structure and existing UI patterns first.
- Keep ownership of data, form state, and UI state explicit.
- Prefer local conventions over generic component abstractions.

### Preferred Patterns

- Clear separation between server data, client UI state, and form state.
- API integration patterns that match nearby code.
- Intentional component boundaries.

### Anti-Patterns

- One-off state models that fight the rest of the app.
- New UI abstractions without local precedent.
- Mixing API, form, and display concerns into one oversized component.

### Checklist

- Identify the routing and component boundary first.
- Confirm where server data and client state already live.
- Apply the React, Next.js, and TypeScript snippets that match the touched boundaries.

---

### UI Ownership

- Identify where server data, validated form state, and local UI state already live.
- Keep components small enough that ownership is obvious.
- Reuse the current API integration and state patterns before introducing a new one.

## React

React patterns for state ownership, forms, hooks, server state, and anti-pattern checks.

### When To Use

Use for React component structure, state ownership, forms, hooks, server state, client state, and React-focused review.

### Core Rules

- Inspect the existing component and state ownership patterns first.
- Keep fetched data, form state, and local UI state separated.
- Read the complete React topic, then apply only the sections relevant to the touched component.

### Preferred Patterns

- Focused components with explicit props and boundaries.
- Clear state ownership.
- Validation and form composition that match nearby code.

### Anti-Patterns

- Duplicating server data in unrelated client state.
- Ad hoc multi-field state for non-trivial forms when the repo has a better pattern.
- Applying unrelated React patterns merely because they share this topic document.

### Checklist

- Identify the state ownership problem first.
- Check existing form and server-state patterns.
- Validate the specific interaction that changed.

---

### React State Decision Matrix

Use this section before writing React or Next.js feature state.

#### Rules

- Use `zod` to validate or parse input and infer types where practical.
- Use `react-hook-form` with `zodResolver` for multi-field validated forms.
- Use `@tanstack/react-query` for remote reads, mutations, cache lifecycle, loading states, and invalidation.
- Use `zustand` for shared client-only UI or workflow state that spans multiple components.
- Use component state for simple local toggles and throwaway inputs.

---

### React Server State

Use this section when a React or Next.js feature reads or mutates remote data.

#### Rules

- Use TanStack React Query for async server data, cache lifecycle, loading states, invalidation, and mutations.
- Use stable query keys that match the resource and relevant filters.
- Invalidate or update the affected query after successful mutations.
- Do not store fetched server data in Zustand.
- Keep API functions reusable and typed; do not mix caching logic into components.

#### Example

```tsx
const usersQuery = useQuery({
  queryKey: ["users"],
  queryFn: getUsers,
  staleTime: 30_000,
})

const createUserMutation = useMutation({
  mutationFn: createUser,
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: ["users"] })
  },
})
```

---

### React Client State

Use this section when state must be shared across client components and is not server data or form state.

#### Rules

- Use Zustand for shared client-only UI or workflow state.
- Keep purely local UI state in the component instead of promoting it to Zustand.
- Keep stores small and focused.
- Use selectors at call sites when that prevents unnecessary renders.
- Do not use Zustand as a general replacement for React Query.

#### Example

```tsx
type FilterStore = {
  search: string
  setSearch: (search: string) => void
}

export const useFilterStore = create<FilterStore>((set) => ({
  search: "",
  setSearch: (search) => set({ search }),
}))
```

---

### React Forms

Use this section when a React feature has non-trivial form validation.

#### Rules

- Define the `zod` schema first when the feature needs validation, parsing, or a reusable client-side contract.
- Infer TypeScript types from schemas instead of duplicating types by hand.
- Use `react-hook-form` with `zodResolver` for multi-field validated forms.
- Keep simple one-field or throwaway inputs in local component state when form tooling would be unnecessary overhead.
- Use shadcn form primitives when the project uses shadcn UI.

#### Example

```tsx
const profileSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
})

type ProfileFormValues = z.infer<typeof profileSchema>

const form = useForm<ProfileFormValues>({
  resolver: zodResolver(profileSchema),
  defaultValues: { name: "", email: "" },
})
```

---

### React Anti Patterns

Use this section as a negative checklist for React and Next.js feature code.

#### Rules

- Do not cache API response bodies in Zustand.
- Do not mirror React Query results into Zustand unless there is a narrowly justified integration boundary.
- Do not use React Query for purely local UI state.
- Do not wrap a trivial single search input in `react-hook-form`.
- Do not create a `zod` schema and then manually duplicate its type definitions unless a library boundary makes that unavoidable.
- Do not create broad stores when a narrow selector-based Zustand store will do.
- Add `"use client"` only where forms, query providers, Zustand consumers, or interactive UI require it.
