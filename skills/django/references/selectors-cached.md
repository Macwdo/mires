---
name: selectors-cached
description: "Mires Django cached selector guidance. Use for read-through caches, hot lookup paths, serialized payload caches, timeout constants, and avoiding cached live ORM instances."
---

# Django Selectors Cached

Use this skill when the same Django read path is hot and the repo already uses caching for similar lookups.

## Rules

- Keep cache reads and writes inside the selector when caching is only a read optimization.
- Prefer caching a read model or serialized payload instead of a live ORM instance unless the repo already caches model instances intentionally.
- Use explicit cache keys and timeout constants.
- Return the same shape on cache hits and database misses.
- Do not hide business side effects inside a cached selector.
