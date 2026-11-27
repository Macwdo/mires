# WSGI Web Entrypoint

## Purpose and when to use it

Use this process entrypoint in a synchronous REST container.

## Complete canonical artifact

<!-- artifact: scripts/webserver.sh; profiles: base -->
```sh
#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec gunicorn \
  --chdir "$project_dir/src" \
  --config "$project_dir/gunicorn.conf.py" \
  core.wsgi:application
```

## Responsibilities and invariants

Migrations run as a separate release job. `exec` ensures signals reach Gunicorn.

## Required tests

Check shell syntax and graceful container termination.
