# Tables and URL-backed filters

Use a semantic table when the information is relational. Keep the desktop table
unless a product requirement explicitly calls for a different mobile
representation; horizontal overflow is often more faithful than silently
removing columns.

Search, filters, sort, page, page size, and selected tab are shareable state and
belong in `searchParams`. Parse them on the server, bound page sizes, allowlist
sort columns, and emit links or GET forms that preserve unrelated parameters.

Requirements:

- a caption or nearby named heading;
- header cells with the correct scope;
- a visible sort label and `aria-sort` on the active header;
- explicit loading, empty, error, and retry rows;
- stable row keys;
- row actions that remain keyboard reachable;
- pagination links with an accessible navigation label;
- no state-changing action on row click alone.

The executable [data recipe](data.md) demonstrates URL search, pagination,
loading, empty, error, retry, mutation, and cache invalidation.
