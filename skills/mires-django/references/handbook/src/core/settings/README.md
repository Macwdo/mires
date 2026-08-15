# Settings Package

## Purpose and when to use it

Use this package, not a single module, as `DJANGO_SETTINGS_MODULE`. Each file
owns one concern; this index only aggregates them in a fixed, alphabetical
import order so every value is defined exactly once and easy to locate.

## When not to use it

Do not add environment-conditional settings files (`local.py`,
`production.py`, ...). One environment-driven package serves every
environment; see [base](base.md) for the production-safety checks that
replace per-environment modules.

## Responsibilities and invariants

Every submodule may import concrete names from `.base` (for example
`SECRET_KEY`, `IS_PRODUCTION`, `module_exists`); nothing outside `base.py`
introduces new cross-module state. `INSTALLED_APPS` and `MIDDLEWARE` are
built once in `base.py` and only ever appended to or mutated in place by a
later submodule (see [cors](cors.md)), never rebuilt, so the aggregator's
import order does not change the final app or middleware list.

## Complete canonical artifact

<!-- artifact: src/core/settings/__init__.py; profiles: base -->
```python
from .base import *  # noqa: F401,F403
from .celery import *  # noqa: F401,F403
from .channels import *  # noqa: F401,F403
from .cors import *  # noqa: F401,F403
from .database import *  # noqa: F401,F403
from .email import *  # noqa: F401,F403
from .jwt import *  # noqa: F401,F403
from .logging import *  # noqa: F401,F403
from .openai import *  # noqa: F401,F403
from .rest_framework import *  # noqa: F401,F403
from .security import *  # noqa: F401,F403
from .sentry import *  # noqa: F401,F403
from .storage import *  # noqa: F401,F403
```

## Alternatives and trade-offs

A single flat `settings.py` has no import graph to reason about but grows
into one screen-scrolling file mixing unrelated concerns. Splitting by
concern costs one aggregator and a handful of small cross-imports from
`base.py`; `ty`/Ruff still resolve every name because each submodule exports
concrete top-level names, not a dynamic namespace.

## Required tests

Import `core.settings` without configured external services, with every
optional dependency present, and with every optional dependency absent.
Confirm `python -c "from core.settings import INSTALLED_APPS"` includes
`corsheaders` exactly once.

## Related standards

See [base](base.md), [reconstruction](../../../docs/reconstruction.md), and
[environment](../../../environment.md).
