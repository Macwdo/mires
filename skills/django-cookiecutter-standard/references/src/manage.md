# Django Management Entry Point

## Purpose and when to use it

Use this artifact for local management commands, migration jobs, checks, and the development server.

## When not to use it

Production web processes should invoke Gunicorn or Daphne directly.

## Responsibilities and invariants

The entry point sets only the settings module and delegates to Django. Configuration belongs in the environment and `core.settings`.

## Complete canonical artifact

<!-- artifact: src/manage.py; profiles: base -->
```python
#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

## Alternatives and trade-offs

Framework-specific wrappers add no value here. Keep this file conventional.

## Required tests

Run `python src/manage.py check` and the migration drift check.

## Related standards

See [settings](core/settings/README.md) and [operations](../docs/operations.md).
