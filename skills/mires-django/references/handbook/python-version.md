# Python Version

## Purpose and when to use it

The handbook snapshot targets Python 3.14.6.

## Complete canonical artifact

<!-- artifact: .python-version; profiles: base -->
```text
3.14.6
```

## Responsibilities and invariants

CI, containers, local `uv`, Ruff, and `ty` target the same Python line.

## Required tests

Run `python --version` in each derived environment.
