# Data fetching

Fetch in a Server Component when data is needed to render a route and no
client-side cache coordination is required. Keep loading and error boundaries
near the route segment they protect.

Use the client only when the experience requires at least one of:

- optimistic or repeated mutations;
- shared cache invalidation across mounted views;
- retry without navigation;
- background refresh;
- polling controlled by visibility or focus.

The [typed API recipe](../recipes/data.md) shows the justified TanStack Query
case. Query keys include every input that changes the response. Mutations
invalidate the narrowest stable key. External responses are parsed with Zod
before entering feature code.

Filters, searches, pagination, and shareable tabs belong in the URL. Parse and
bound them on the server. Never mirror the same canonical value in the URL, a
global store, and component state.
