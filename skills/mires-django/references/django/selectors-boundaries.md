---
name: selectors-boundaries
description: "Mires Django selector boundary guidance. Use for separating reads from writes, composing selectors, naming selectors, module layout, and avoiding side effects in read paths."
---

# Django Selectors Boundaries

Use this skill when deciding what belongs in a selector.

## Rules

- Selectors may compose other selectors.
- Selectors do not mutate database state or trigger business side effects.
- Selectors may populate a cache on a read miss when that cache write is only a read optimization.
- Services may call selectors to enforce read-side rules before mutating data.
- Endpoints may use selectors directly for read-only flows.
- Prefer names such as `invoice_get`, `invoice_list`, or `invoice_get_visible_for`.
- Start with `selectors.py`; split into a `selectors/` package when query surface grows by domain.
