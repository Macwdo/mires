---
name: macwdo-reviewer
description: "Review code changes against Macwdo conventions. Use when the user asks for a review, PR review, architecture review, implementation review, or validation against Macwdo Python, Django, LangGraph, React, Next.js, agent-testing, FastAPI, Postgres, Alembic, Celery, Docker Compose, service-layer, or DevEx patterns."
---

# Macwdo Reviewer

Use this skill to perform a findings-first review against the relevant Macwdo pattern skills. This is a review router, not an implementation guide.

## Workflow

1. Identify the review scope from the user request, git diff, PR context, or named files.
2. Load `macwdo-explorer` first when the relevant pattern family is not obvious.
3. Load every relevant Macwdo leaf skill for the code under review before judging pattern compliance.
4. Inspect the changed code directly. Prefer `rg`, `git diff`, targeted file reads, and existing test output over broad speculation.
5. Use `macwdo-researcher` before relying on external dependency behavior, framework rules, security implications, current APIs, or best-practice claims.
6. Report bugs, regressions, missing tests, pattern violations, and maintainability risks in severity order.

## Pattern Coverage

Use all Macwdo patterns that apply to the touched surface:

- Generic Python: functions, typing, dependency boundaries, state mutation, errors, module shape, validation, tests, and test helpers.
- Django: models, migrations, services, selectors, serializers, endpoints, routing, response shape, DRF tests, and project bootstrap patterns.
- LangGraph: state, services, node factories, service-node pattern, graph assembly, and LLM nodes.
- React and Next.js: state ownership, forms, server state, client state, anti-patterns, server-first Next.js, project bootstrap, React Query, axios, Zustand, and form setup.
- Infrastructure and backend support: FastAPI, Postgres, Alembic, Celery, Docker Compose, service-layer, DevEx, and agent-testing skills.

Do not load unrelated leaf skills just to be exhaustive. "All Macwdo patterns" means all patterns relevant to the changed code.

## Review Output

Lead with findings. Use this structure:

1. Findings, ordered by severity, with file and line references when possible.
2. Open questions or assumptions, only when they affect correctness.
3. Test gaps or verification notes.
4. Brief summary, only after findings.

If there are no issues, say that clearly and still mention any residual risk or tests not run.

## Standards

- Treat Macwdo leaf skills as the source of truth for local conventions.
- Prefer concrete behavioral risks over style-only comments.
- Flag missing tests when the changed behavior crosses a meaningful boundary or risk surface.
- Avoid proposing broad refactors unless they are necessary to prevent a concrete defect.
- Do not make code changes during review unless the user explicitly asks for fixes.
