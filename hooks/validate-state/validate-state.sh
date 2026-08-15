#!/usr/bin/env bash
# Re-validate the Mires catalog after an edit touches state.yml or a catalog directory.
# Fails open: a broken hook must never block editing.
set -uo pipefail

input=$(cat)

edited_path=$(printf '%s' "$input" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)
print(payload.get("file_path") or "")
' 2>/dev/null)

case "$edited_path" in
  *state.yml|*/skills/*|*/subagents/*|*/rules/*|*/mcps/*|*/hooks/*) ;;
  *) exit 0 ;;
esac

if ! command -v uv >/dev/null 2>&1; then
  exit 0
fi

if ! output=$(uv run mires validate 2>&1); then
  printf 'Mires catalog validation failed after editing %s:\n%s\n' "$edited_path" "$output" >&2
fi

exit 0
