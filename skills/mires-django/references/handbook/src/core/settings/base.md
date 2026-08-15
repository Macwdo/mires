# Core Django Settings

## Purpose and when to use it

Use this module for the settings package's shared foundation: paths, the
`module_exists` optional-dependency probe, the environment/secret/host
knobs every other submodule reads, installed apps, middleware, URLconf, and
templates.

## When not to use it

Do not add a setting here that only one other submodule needs; give that
setting its own file and import the shared value from here instead.

## Responsibilities and invariants

Local defaults are non-public and usable without external services.
Production configuration fails before Django starts when required security
values are absent. `INSTALLED_APPS` and `MIDDLEWARE` are built as lists so
later submodules (see [cors](cors.md)) can append or insert into them in
place.

Optional application discovery uses `module_exists`, the same pattern
[celery](celery.md), [channels](channels.md), and [sentry](sentry.md) use to
stay importable whether or not their package is part of the resolved
reconstruction.

## Complete canonical artifact

<!-- artifact: src/core/settings/base.py; profiles: base -->
```python
from __future__ import annotations

import importlib.util
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BASE_DIR.parent


def module_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


ENVIRONMENT = config("ENVIRONMENT", default="local").strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG = config("DEBUG", default=False, cast=bool)

development_secret = "local-only-change-me-000000000000000000000000000000"
SECRET_KEY = config("SECRET_KEY", default=development_secret)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
DATABASE_URL = config("DATABASE_URL", default=None)

if IS_PRODUCTION:
    errors: list[str] = []
    if DEBUG:
        errors.append("DEBUG must be false")
    if development_secret == SECRET_KEY or len(SECRET_KEY) < 50:
        errors.append("SECRET_KEY must be a unique value of at least 50 characters")
    if not config("ALLOWED_HOSTS", default=""):
        errors.append("ALLOWED_HOSTS must be explicit")
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    if errors:
        raise ImproperlyConfigured("Invalid production settings: " + "; ".join(errors))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "apps.common",
    "apps.account",
    "apps.authentication",
    "apps.api",
    "apps.customer",
]

OPTIONAL_APPLICATIONS = (
    "apps.jobs",
    "apps.files",
    "apps.realtime",
    "apps.documents",
    "apps.membership",
)
for optional_application in OPTIONAL_APPLICATIONS:
    if module_exists(optional_application):
        INSTALLED_APPS.append(optional_application)

if module_exists("channels"):
    INSTALLED_APPS.append("channels")
if module_exists("django_celery_results"):
    INSTALLED_APPS.append("django_celery_results")
if module_exists("django_celery_beat"):
    INSTALLED_APPS.append("django_celery_beat")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.api.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "authentication.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_DIR / "media"

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
```

## Alternatives and trade-offs

SQLite is a safe local convenience, not a substitute for PostgreSQL
integration tests; [database](database.md) owns that decision. Dynamic
optional app discovery lets this module remain importable across profiles;
capability-specific behavior must still be explicitly enabled by its URLs
and workers.

## Required tests

Test environment parsing, production failure cases, Django checks, deploy
checks, and settings import without optional dependencies.

## Related standards

See [database](database.md), [security](security.md),
[API design](../../../docs/api-design.md),
[security standards](../../../docs/security.md), and
[environment](../../../environment.md).
