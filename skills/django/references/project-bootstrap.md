---
name: project-bootstrap
description: "Mires Django project bootstrap guidance. Use to start a fresh Django backend from Mires cookiecutter, prefer HTTPS, fall back to SSH only when needed, and stop after generation."
---

# Django Project Bootstrap

Use this skill when the user wants a fresh Django codebase or backend/API project from the personal template.

## Rules

- Template repo: `https://github.com/Mires/django-cookiecutter-standard`.
- Prefer HTTPS and use `git@github.com:Mires/django-cookiecutter-standard.git` only when SSH access is required.
- Generate a new project directory without editing the template repository.
- Do not install dependencies, create virtualenvs, run migrations, or start services unless the user asks.
- If template variables are already known, prefer a non-interactive invocation with explicit key/value overrides.
- Ask only for missing project-specific fields when the template prompts for values not provided.

## Workflow

1. Run Cookiecutter directly against the HTTPS URL.
2. If `cookiecutter` is missing and `uvx` exists, run it through `uvx --from cookiecutter`.
3. If HTTPS is blocked by required SSH access, verify SSH with `git ls-remote` before retrying.
4. Verify the expected output directory exists and stop after bootstrap.

## Commands

```bash
cookiecutter https://github.com/Mires/django-cookiecutter-standard
uvx --from cookiecutter cookiecutter https://github.com/Mires/django-cookiecutter-standard
git ls-remote git@github.com:Mires/django-cookiecutter-standard.git HEAD
```
