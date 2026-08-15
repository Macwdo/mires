# Database Configuration

## Purpose and when to use it

Use `database_config` to translate one `DATABASE_URL` into Django's
`DATABASES` shape, accepting SQLite or PostgreSQL.

## When not to use it

Do not read individual `DB_*` variables; a single URL keeps local, test, and
production configuration in one value.

## Responsibilities and invariants

An absent `DATABASE_URL` falls back to a local SQLite file, never to a
guessed PostgreSQL host. A malformed or unsupported scheme fails fast with
`ImproperlyConfigured` instead of producing a partially valid config.

## Complete canonical artifact

<!-- artifact: src/core/settings/database.py; profiles: base -->
```python
from __future__ import annotations

from urllib.parse import parse_qsl, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

from .base import DATABASE_URL, PROJECT_DIR


def database_config(raw_url: str | None) -> dict[str, object]:
    if not raw_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": PROJECT_DIR / "db.sqlite3",
        }

    parsed = urlparse(raw_url)
    if parsed.scheme == "sqlite":
        if not parsed.path:
            raise ImproperlyConfigured("DATABASE_URL must include a SQLite path")
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": unquote(parsed.path),
        }
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_URL must use sqlite or postgresql")

    options = dict(parse_qsl(parsed.query))
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
        "CONN_MAX_AGE": 60,
        "OPTIONS": options,
    }


DATABASES = {"default": database_config(DATABASE_URL)}
```

## Alternatives and trade-offs

SQLite is a safe local convenience, not a substitute for PostgreSQL
integration tests.

## Required tests

Test SQLite fallback, a PostgreSQL URL with credentials and query options,
and rejection of an unsupported scheme.

## Related standards

See [base](base.md) and [testing](../../../docs/testing.md).
