---
name: macwdo-typescript-react-client-state
description: "Macwdo React client-state guidance. Use for focused Zustand stores, shared client-only workflow state, selectors, local component state boundaries, and avoiding broad stores."
---

# React Client State

Use this skill when state must be shared across client components and is not server data or form state.

## Rules

- Use Zustand for shared client-only UI or workflow state.
- Keep purely local UI state in the component instead of promoting it to Zustand.
- Keep stores small and focused.
- Use selectors at call sites when that prevents unnecessary renders.
- Do not use Zustand as a general replacement for React Query.

## Example

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
