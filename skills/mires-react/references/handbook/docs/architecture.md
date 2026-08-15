# Architecture

## Default rendering model

App Router modules are Server Components unless they declare `"use client"`.
Keep that directive at the leaf that owns browser APIs, local interaction, or
effects. Pass serializable data and server actions through that boundary rather
than promoting a route or layout to the client.

Routes coordinate. Feature modules own product behavior. Reusable primitives
own visual and interaction contracts without importing features. Libraries own
boundary concerns such as runtime parsing, sessions, and transports.

```text
src/app -> src/features -> src/components
   |            |
   +----------> src/lib
```

Dependencies do not point from shared primitives back into features or routes.

## State ownership

Prefer, in order:

1. Values derived during render.
2. Local component state for local interaction.
3. URL state for shareable filters, searches, pagination, and tabs.
4. Server state in Server Components.
5. TanStack Query when a client interaction needs shared caching,
   invalidation, retry, or background refresh.
6. Global client state only when unrelated feature boundaries genuinely share
   mutable client state.

Do not synchronize derived state in an effect. Effects connect React to an
external system and must return cleanup when they allocate a subscription,
timer, observer, or transport.

## Deliberate omissions

There is no default repository, use-case, service, container, global store, or
generic component facade. Add an abstraction only after repeated behavior and a
stable boundary are visible.

Related: [component design](component-design.md),
[data fetching](data-fetching.md), and [conventions](conventions.md).
