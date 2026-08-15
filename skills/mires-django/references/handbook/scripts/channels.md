# Daphne ASGI Entrypoint

## Purpose and when to use it

Use Daphne for HTTP, SSE, and WebSockets whenever `realtime-sse` or `realtime-channels` is part of the resolved reconstruction — this entrypoint works for either alone.

## Complete canonical artifact

<!-- artifact: scripts/channels.sh; profiles: realtime-sse,realtime-channels,realtime,full -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir/src"
exec daphne \
  --bind "${DAPHNE_BIND:-0.0.0.0}" \
  --port "${DAPHNE_PORT:-8000}" \
  core.asgi:application
```

## Responsibilities and invariants

TLS and request limits belong at the trusted reverse proxy.

## Required tests

Check shell syntax and smoke-test HTTP plus a WebSocket handshake.
