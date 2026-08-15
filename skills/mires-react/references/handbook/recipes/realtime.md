# Realtime recipe

Realtime connections are client-only resources with explicit ownership.
Consumers cancel them on unmount, reconnect with bounded backoff, ignore
duplicate events, preserve server sequence order, and validate every message.

Use SSE for one-way server updates and WebSockets only when bidirectional,
low-latency communication is necessary.

<!-- artifact: src/lib/realtime.ts; profiles: realtime,full -->
```ts
import { z } from "zod";

export const realtimeEventSchema = z.object({
  id: z.string().min(1),
  sequence: z.number().int().nonnegative(),
  message: z.string().min(1),
});

export type RealtimeEvent = z.infer<typeof realtimeEventSchema>;

export function parseRealtimeEvent(value: string) {
  try {
    const parsed = realtimeEventSchema.safeParse(JSON.parse(value));
    return parsed.success ? parsed.data : null;
  } catch {
    return null;
  }
}

export function mergeRealtimeEvent(current: RealtimeEvent[], candidate: unknown) {
  const parsed = realtimeEventSchema.safeParse(candidate);
  if (!parsed.success || current.some((event) => event.id === parsed.data.id)) {
    return current;
  }
  return [...current, parsed.data].sort((left, right) => left.sequence - right.sequence);
}

type Source = {
  addEventListener(
    type: "message" | "error",
    listener: (event: MessageEvent | Event) => void,
  ): void;
  close(): void;
};

type Socket = {
  addEventListener(type: "message", listener: (event: MessageEvent) => void): void;
  close(code?: number, reason?: string): void;
};

export function startEventStream({
  createSource = (url: string) => new EventSource(url),
  onEvent,
  reconnectAfterMs = 1_000,
  schedule = (callback, delay) => window.setTimeout(callback, delay),
  url,
}: {
  createSource?: (url: string) => Source;
  onEvent: (event: RealtimeEvent) => void;
  reconnectAfterMs?: number;
  schedule?: (callback: () => void, delay: number) => number;
  url: string;
}) {
  let source: Source | null = null;
  let reconnectTimer: number | null = null;
  let stopped = false;

  const connect = () => {
    if (stopped) return;
    source = createSource(url);
    source.addEventListener("message", (event) => {
      if (!(event instanceof MessageEvent)) return;
      const parsed = parseRealtimeEvent(String(event.data));
      if (parsed) onEvent(parsed);
    });
    source.addEventListener("error", () => {
      source?.close();
      reconnectTimer = schedule(connect, reconnectAfterMs);
    });
  };

  connect();

  return () => {
    stopped = true;
    source?.close();
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer);
    }
  };
}

export function openValidatedSocket({
  createSocket = (url: string) => new WebSocket(url),
  onEvent,
  url,
}: {
  createSocket?: (url: string) => Socket;
  onEvent: (event: RealtimeEvent) => void;
  url: string;
}) {
  const socket = createSocket(url);
  socket.addEventListener("message", (event) => {
    const parsed = parseRealtimeEvent(String(event.data));
    if (parsed) onEvent(parsed);
  });
  return () => socket.close(1000, "Component unmounted");
}
```

<!-- artifact: src/features/realtime/realtime-status.tsx; profiles: realtime,full -->
```tsx
"use client";

import { useEffect, useState } from "react";

import { mergeRealtimeEvent, type RealtimeEvent, startEventStream } from "@/lib/realtime";

export function RealtimeStatus() {
  const [events, setEvents] = useState<RealtimeEvent[]>([]);

  useEffect(
    () =>
      startEventStream({
        url: "/api/events",
        reconnectAfterMs: 5_000,
        onEvent: (event) => setEvents((current) => mergeRealtimeEvent(current, event)),
      }),
    [],
  );

  return (
    <section aria-labelledby="realtime-title">
      <h2 id="realtime-title">Realtime status</h2>
      <p aria-live="polite">
        {events.length ? `${events.length} updates received.` : "Connecting…"}
      </p>
      <ol>
        {events.map((event) => (
          <li key={event.id}>{event.message}</li>
        ))}
      </ol>
    </section>
  );
}
```

<!-- artifact: src/app/realtime/page.tsx; profiles: realtime,full -->
```tsx
import { RealtimeStatus } from "@/features/realtime/realtime-status";

export default function RealtimePage() {
  return (
    <main id="main" className="shell">
      <h1>Realtime lifecycle</h1>
      <RealtimeStatus />
    </main>
  );
}
```

<!-- artifact: src/app/api/events/route.ts; profiles: realtime,full -->
```ts
export const dynamic = "force-dynamic";

export function GET(request: Request) {
  const encoder = new TextEncoder();
  let closed = false;
  const stream = new ReadableStream({
    start(controller) {
      const events = [
        { id: "ready", sequence: 1, message: "Connection ready" },
        { id: "synced", sequence: 2, message: "Reference synchronized" },
      ];
      for (const event of events) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
      }
      controller.close();
      closed = true;
      request.signal.addEventListener(
        "abort",
        () => {
          if (!closed) controller.close();
        },
        { once: true },
      );
    },
  });

  return new Response(stream, {
    headers: {
      "Cache-Control": "no-cache, no-transform",
      "Content-Type": "text/event-stream",
      Connection: "keep-alive",
    },
  });
}
```
