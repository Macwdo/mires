---
name: macwdo-typescript-next-axios-setup
description: "Macwdo Next.js axios setup guidance. Use for a shared src/lib axios instance, centralized base configuration, simple defaults, and avoiding invented interceptors or duplicate clients."
---

# Next Axios Setup

Use this skill when adding HTTP client wiring to a Next.js app.

## Rules

- Create a shared axios instance in a small `lib` module such as `src/lib/axios.ts`.
- Centralize base configuration there so React Query hooks import the same client.
- Keep the instance simple by default.
- Do not invent interceptors, auth headers, or environment handling unless the task requires them.
- Do not create multiple competing API clients.
