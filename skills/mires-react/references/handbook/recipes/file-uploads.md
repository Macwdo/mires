# File uploads

Authorize before reading a body. Enforce request and per-file size limits at the
reverse proxy and application. Allowlist MIME type and extension, generate the
storage name server-side, scan untrusted content, and store it outside the
public web root. Never trust the browser-provided path or MIME type.

The canonical endpoint validates one small text file and returns metadata only;
an application must replace the final boundary with reviewed private storage.

<!-- artifact: src/app/api/uploads/route.ts; profiles: full -->
```ts
import { NextResponse } from "next/server";
import { z } from "zod";

const metadataSchema = z.object({
  name: z
    .string()
    .min(1)
    .max(120)
    .regex(/^[a-zA-Z0-9._-]+$/),
  type: z.literal("text/plain"),
  size: z.number().int().positive().max(1_000_000),
});

export async function POST(request: Request) {
  const declaredLength = Number(request.headers.get("content-length") ?? 0);
  if (declaredLength > 1_100_000) {
    return NextResponse.json({ message: "Upload is too large." }, { status: 413 });
  }

  const body = await request.formData();
  const candidate = body.get("file");
  if (!(candidate instanceof File)) {
    return NextResponse.json({ message: "Choose one file." }, { status: 400 });
  }

  const metadata = metadataSchema.safeParse({
    name: candidate.name,
    type: candidate.type,
    size: candidate.size,
  });
  if (!metadata.success) {
    return NextResponse.json(
      { message: "File type, name, or size is not allowed." },
      { status: 415 },
    );
  }

  return NextResponse.json(
    {
      accepted: true,
      metadata: metadata.data,
      storage: "Connect reviewed private storage at this server boundary.",
    },
    { status: 202 },
  );
}
```
