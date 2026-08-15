# Environment boundaries

Server variables are parsed in a server-only module. Browser variables have a
separate schema and must be explicitly public. Never copy a credential into a
`NEXT_PUBLIC_*` variable.

<!-- artifact: .env.example; profiles: base,forms,data,auth,realtime,full -->
```dotenv
NEXT_PUBLIC_APP_NAME=Frontend Standards
APP_ORIGIN=http://127.0.0.1:3000
SESSION_SECRET=
```

<!-- artifact: src/lib/env/server.ts; profiles: base,forms,data,auth,realtime,full -->
```ts
import "server-only";

import { z } from "zod";

const serverSchema = z.object({
  APP_ORIGIN: z.url().default("http://127.0.0.1:3000"),
  SESSION_SECRET: z.string().min(32).optional(),
});

export const serverEnv = serverSchema.parse({
  APP_ORIGIN: process.env.APP_ORIGIN,
  SESSION_SECRET: process.env.SESSION_SECRET || undefined,
});
```

<!-- artifact: src/lib/env/client.ts; profiles: base,forms,data,auth,realtime,full -->
```ts
import { z } from "zod";

const clientSchema = z.object({
  NEXT_PUBLIC_APP_NAME: z.string().min(1).default("Frontend Standards"),
});

export const clientEnv = clientSchema.parse({
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
});
```
