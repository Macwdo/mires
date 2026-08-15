# Validate State

Runs `mires validate` after an edit touches `state.yml` or any catalog directory, so a broken catalog surfaces immediately instead of at install time.

## Behavior

- Event: `afterFileEdit`.
- Filters on the edited path; unrelated edits exit immediately.
- Fails open. A missing `uv` or a crashing hook never blocks editing; validation failures are reported on stderr.

## Install

Copy `hooks.json` into the consuming project's `.cursor/hooks.json` and this directory into `.cursor/hooks/`, then adjust the `command` path. Cursor resolves project hook commands relative to the project root.
