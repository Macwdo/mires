# Performance

Measure before optimizing.

- Keep Server Components as the default to reduce browser JavaScript.
- Place client boundaries around interaction owners, not whole routes.
- Stream slow route segments with Suspense and meaningful loading UI.
- Fetch independent resources concurrently.
- Use framework image and font optimizations where applicable.
- Dynamically import genuinely heavy, infrequently used client features.
- Virtualize only measured large collections.
- Avoid effects and state that merely duplicate render-time derivation.
- Stabilize context values only when profiling shows dependent rerenders matter.
- Bound realtime buffers, retries, and reconnect backoff.

Track Core Web Vitals against product budgets, together with route bundle size
and server latency. A faster empty shell is not useful if the interaction is
inaccessible or data remains stale.
