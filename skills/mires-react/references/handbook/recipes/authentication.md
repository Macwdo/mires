# Authentication recipe

Authentication is server-owned. A browser receives only an opaque, signed,
`HttpOnly` session cookie. Authorization is repeated at every protected server
entry point; hiding a control is never authorization. Replace the illustrative
identity-verification boundary with a reviewed provider or application service.

Redirect destinations are constrained to local paths. State-changing Route
Handlers must validate an anti-CSRF token; Server Actions should additionally
enforce an expected origin at the deployment boundary.

<!-- artifact: src/features/auth/model.ts; profiles: auth,full -->
```ts
import { createHmac, timingSafeEqual } from "node:crypto";

import { z } from "zod";

const sessionPayloadSchema = z.object({
  userId: z.string().min(1),
  expiresAt: z.number().int().positive(),
});

export type Session = z.infer<typeof sessionPayloadSchema>;

function signature(payload: string, secret: string) {
  return createHmac("sha256", secret).update(payload).digest("base64url");
}

export function encodeSession(session: Session, secret: string) {
  const payload = Buffer.from(JSON.stringify(session), "utf8").toString("base64url");
  return `${payload}.${signature(payload, secret)}`;
}

export function decodeSession(value: string, secret: string, now = Date.now()): Session | null {
  const [payload, suppliedSignature, extra] = value.split(".");
  if (!payload || !suppliedSignature || extra) {
    return null;
  }

  const expectedSignature = signature(payload, secret);
  const supplied = Buffer.from(suppliedSignature);
  const expected = Buffer.from(expectedSignature);
  if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
    return null;
  }

  try {
    const session = sessionPayloadSchema.parse(
      JSON.parse(Buffer.from(payload, "base64url").toString("utf8")),
    );
    return session.expiresAt > now ? session : null;
  } catch {
    return null;
  }
}

export function safeRedirect(value: string | null | undefined, fallback = "/protected") {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) {
    return fallback;
  }
  return value;
}

export function isValidCsrfToken(cookieToken: string | undefined, submittedToken: string | null) {
  if (!cookieToken || !submittedToken) {
    return false;
  }
  const cookie = Buffer.from(cookieToken);
  const submitted = Buffer.from(submittedToken);
  return cookie.length === submitted.length && timingSafeEqual(cookie, submitted);
}
```

<!-- artifact: src/features/auth/session.ts; profiles: auth,full -->
```ts
import "server-only";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { decodeSession, encodeSession } from "@/features/auth/model";
import { serverEnv } from "@/lib/env/server";

const cookieName = "__Host-session";
const maxAgeSeconds = 60 * 60 * 8;

function sessionSecret() {
  if (!serverEnv.SESSION_SECRET) {
    throw new Error("SESSION_SECRET must be configured before authentication is enabled.");
  }
  return serverEnv.SESSION_SECRET;
}

export async function readSession() {
  const value = (await cookies()).get(cookieName)?.value;
  if (!value) {
    return null;
  }
  return decodeSession(value, sessionSecret());
}

export async function requireSession(nextPath = "/protected") {
  const session = await readSession();
  if (!session) {
    redirect(`/login?next=${encodeURIComponent(nextPath)}`);
  }
  return session;
}

export async function establishSession(userId: string) {
  const value = encodeSession(
    { userId, expiresAt: Date.now() + maxAgeSeconds * 1000 },
    sessionSecret(),
  );
  (await cookies()).set(cookieName, value, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: maxAgeSeconds,
  });
}

export async function clearSession() {
  (await cookies()).set(cookieName, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });
}
```

<!-- artifact: src/app/protected/page.tsx; profiles: auth,full -->
```tsx
import { requireSession } from "@/features/auth/session";

export default async function ProtectedPage() {
  const session = await requireSession("/protected");

  return (
    <main id="main" className="shell">
      <h1>Protected route</h1>
      <p>Authenticated as {session.userId}.</p>
    </main>
  );
}
```

<!-- artifact: src/app/login/page.tsx; profiles: auth,full -->
```tsx
import Link from "next/link";

import { safeRedirect } from "@/features/auth/model";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const nextPath = safeRedirect((await searchParams).next);

  return (
    <main id="main" className="shell">
      <h1>Sign in required</h1>
      <p>
        Connect this boundary to the application&apos;s reviewed identity provider. After identity
        verification, call <code>establishSession</code> on the server.
      </p>
      <Link href={nextPath}>Continue after authentication</Link>
    </main>
  );
}
```
