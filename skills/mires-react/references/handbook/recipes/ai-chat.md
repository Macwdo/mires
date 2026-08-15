# AI chat interfaces

The browser sends user input only to the application server. Provider
credentials remain in a server-only adapter. Apply authentication,
authorization, rate limits, input limits, output validation, cancellation,
retention policy, and content-safety controls at that boundary. Never log raw
prompts or model responses by default.

The interface uses a labelled transcript, pending state, cancellation, and
focus-safe native controls. The provider adapter is intentionally unavailable
without server-only configuration, so ordinary CI never calls a vendor.

<!-- artifact: src/features/chat/model.ts; profiles: full -->
```ts
import { z } from "zod";

export const chatRequestSchema = z.object({
  message: z.string().trim().min(1).max(2_000),
});

export const chatResponseSchema = z.object({
  reply: z.string().min(1).max(8_000),
});
```

<!-- artifact: src/features/chat/provider.ts; profiles: full -->
```ts
import "server-only";

import { z } from "zod";

import { chatResponseSchema } from "@/features/chat/model";

const providerEnvSchema = z.object({
  AI_PROVIDER_URL: z.url(),
  AI_PROVIDER_API_KEY: z.string().min(20),
});

export async function generateReply(message: string, signal: AbortSignal) {
  const environment = providerEnvSchema.parse({
    AI_PROVIDER_URL: process.env.AI_PROVIDER_URL,
    AI_PROVIDER_API_KEY: process.env.AI_PROVIDER_API_KEY,
  });
  const response = await fetch(environment.AI_PROVIDER_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${environment.AI_PROVIDER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!response.ok) {
    throw new Error(`AI provider failed with status ${response.status}.`);
  }
  return chatResponseSchema.parse(await response.json());
}
```

<!-- artifact: src/app/api/chat/route.ts; profiles: full -->
```ts
import { NextResponse } from "next/server";

import { chatRequestSchema } from "@/features/chat/model";
import { generateReply } from "@/features/chat/provider";

export async function POST(request: Request) {
  const body: unknown = await request.json().catch(() => null);
  const parsed = chatRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ message: "Enter a valid message." }, { status: 400 });
  }

  try {
    return NextResponse.json(await generateReply(parsed.data.message, request.signal));
  } catch {
    return NextResponse.json({ message: "Chat is temporarily unavailable." }, { status: 503 });
  }
}
```

<!-- artifact: src/features/chat/chat-panel.tsx; profiles: full -->
```tsx
"use client";

import { useRef, useState } from "react";

import { chatResponseSchema } from "@/features/chat/model";

export function ChatPanel() {
  const [reply, setReply] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const controller = useRef<AbortController | null>(null);

  async function submit(formData: FormData) {
    const message = String(formData.get("message") ?? "").trim();
    if (!message) return;
    controller.current?.abort();
    controller.current = new AbortController();
    setPending(true);
    setError(null);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
        signal: controller.current.signal,
      });
      const body: unknown = await response.json();
      if (!response.ok) throw new Error("Chat request failed.");
      setReply(chatResponseSchema.parse(body).reply);
    } catch (reason) {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) {
        setError("The assistant could not respond. Try again.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <section aria-labelledby="chat-heading" className="stack">
      <h2 id="chat-heading">Assistant</h2>
      <div aria-label="Conversation transcript" aria-live="polite">
        {reply ? <p>{reply}</p> : <p>No messages yet.</p>}
      </div>
      <form action={submit} className="stack">
        <label htmlFor="chat-message">Message</label>
        <input id="chat-message" name="message" maxLength={2_000} required />
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Sending…" : "Send message"}
        </button>
        {pending ? (
          <button type="button" onClick={() => controller.current?.abort()}>
            Cancel
          </button>
        ) : null}
        {error ? <p role="alert">{error}</p> : null}
      </form>
    </section>
  );
}
```
