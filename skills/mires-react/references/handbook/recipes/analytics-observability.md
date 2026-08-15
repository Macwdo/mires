# Analytics and observability

Collect the minimum event needed for a declared product or operational
question. Name events from a reviewed taxonomy, validate properties, obtain
required consent before client collection, and never attach credentials,
session identifiers, free-form messages, or sensitive fields.

Server logs use a request identifier and structured safe metadata. Error
reporting captures the failing boundary and release, not request bodies.

<!-- artifact: src/app/api/telemetry/route.ts; profiles: full -->
```ts
import { NextResponse } from "next/server";
import { z } from "zod";

const telemetrySchema = z.object({
  event: z.enum(["reference_viewed", "recipe_opened"]),
  path: z.string().startsWith("/").max(200),
});

export async function POST(request: Request) {
  const body: unknown = await request.json().catch(() => null);
  const parsed = telemetrySchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ accepted: false }, { status: 400 });
  }

  console.info("telemetry", { event: parsed.data.event, path: parsed.data.path });
  return new NextResponse(null, { status: 204 });
}
```
