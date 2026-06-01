---
name: server-state
description: "Mires React server-state guidance. Use for TanStack React Query reads, mutations, query keys, invalidation, staleTime, loading/error states, and keeping fetched data out of Zustand."
---

# React Server State

Use this skill when a React or Next.js feature reads or mutates remote data.

## Rules

- Use TanStack React Query for async server data, cache lifecycle, loading states, invalidation, and mutations.
- Use stable query keys that match the resource and relevant filters.
- Invalidate or update the affected query after successful mutations.
- Do not store fetched server data in Zustand.
- Keep API functions reusable and typed; do not mix caching logic into components.

## Example

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
