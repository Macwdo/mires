# Channels Background Worker

## Purpose and when to use it

Use `runworker` only for explicitly routed Channels background messages; it does not replace Celery durability. Requires `realtime-channels` — SSE has no consumer-routed background messages.

## Complete canonical artifact

<!-- artifact: scripts/channels-worker.sh; profiles: realtime-channels,realtime,full -->
```sh
#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
  echo "at least one channel name is required" >&2
  exit 2
fi

exec python src/manage.py runworker "$@"
```

## Responsibilities and invariants

The caller supplies an allowlisted channel name. Durable jobs remain in Celery.

## Required tests

Check shell syntax and route one test message to an explicit channel.
