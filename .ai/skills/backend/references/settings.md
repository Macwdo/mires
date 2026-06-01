---
name: settings
description: "Mires Python settings guidance. Use when adding or changing application configuration, environment handling, Pydantic Settings, Dynaconf, Django settings, dataclass-like config objects, or settings-backed collaborators."
---

# Python Settings

Use this skill when backend work touches application settings or environment configuration.

## Discovery First

Before editing settings, inspect:

- Existing settings modules and imports.
- Framework settings such as Django settings or FastAPI app configuration.
- Dependencies in `pyproject.toml`, lockfiles, or requirements files.
- Environment examples such as `.env.example`, compose files, deployment docs, or README setup steps.
- Tests that override settings or environment values.

## Rules

- Extend the repository's existing settings pattern instead of creating a parallel one.
- Use Pydantic Settings when the project already uses Pydantic Settings.
- Use Dynaconf when the project already uses Dynaconf.
- Use Django settings when the project is a Django project and settings are already centralized there.
- Use existing environment-only helpers when that is the established pattern.
- Do not introduce dataclass-based application settings when Pydantic Settings, Dynaconf, Django settings, or another established settings system exists.
- Do not read environment variables deep inside business logic when the project has a settings boundary.
- Keep settings construction at application, framework, CLI, worker, or dependency boundaries.
- Add new fields to the existing settings object, module, or framework settings surface.
- Keep secret examples as placeholders such as `OPENAI_API_KEY`; do not commit real secrets.

## Review Checklist

- The chosen settings pattern is supported by local evidence.
- New settings live beside existing settings.
- Callers receive settings through the existing dependency, import, or framework pattern.
- Tests or docs are updated when new required environment values are introduced.
- No duplicate configuration object, dataclass config, or ad hoc environment reader was added.
