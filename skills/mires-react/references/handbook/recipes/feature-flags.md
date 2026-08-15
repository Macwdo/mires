# Feature flags

Evaluate authorization-sensitive and server-rendered flags on the server. A
client flag may change presentation but must never grant access. Every flag
needs an owner, rollout plan, safe default, observability, and removal date.

<!-- artifact: src/features/flags/server-flags.ts; profiles: full -->
```ts
import "server-only";

import { z } from "zod";

const flagSchema = z.enum(["on", "off"]).default("off");

export function readServerFlags() {
  return {
    experimentalDashboard: flagSchema.parse(process.env.FEATURE_EXPERIMENTAL_DASHBOARD) === "on",
  } as const;
}
```
