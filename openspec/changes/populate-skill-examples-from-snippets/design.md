## Context

Mires now uses an agent-first `.ai` layout: public routing lives in `.ai/agents`, while detailed implementation guidance lives in `.ai/skills/**/references`. The backend-oriented reference files already define patterns, but several are mostly conceptual. The repository also has `.snippets/python` examples for FastAPI startup, async SQLAlchemy setup, FastAPI dependencies, AWS client helpers, service signatures, Celery, Docker Compose, and Ruff/pyproject configuration.

This change uses those snippets as authoring input for canonical skill references. The implementation should improve concrete examples without changing runtime routing, package installation behavior, or public agent discovery.
After the useful examples are migrated, the implementation should remove the temporary `.snippets` tree so the repository does not retain a second informal example source.

## Goals / Non-Goals

**Goals:**

- Add practical examples to the relevant `.ai/skills/**/references` files.
- Preserve the top-level `SKILL.md` files as concise indexes.
- Keep snippet-derived examples generic enough to serve as guidance across projects.
- Remove `.snippets` after migrating the useful examples into canonical references.
- Validate that reference paths and example-bearing docs remain reachable from the owning skills.

**Non-Goals:**

- Do not keep `.snippets` as a runtime asset tree, public discovery surface, or long-lived parallel example library.
- Do not introduce new public granular skill packages.
- Do not rewrite archived OpenSpec history.
- Do not build or validate a generated FastAPI application from the snippets.

## Decisions

1. Store examples in references, not top-level skill files.

   The existing repository pattern keeps `SKILL.md` files short and routes readers to reference files. Adding examples to references preserves this shape and avoids increasing default context for ordinary agent discovery.

2. Treat snippets as source material, not canonical app code.

   The snippets contain concrete identifiers such as `src.config`, MinIO, LocalStack, and project-specific service names. Reference docs should either adapt those examples to reusable form or clearly frame them as representative snippets. This avoids teaching agents to copy source-specific imports into unrelated repositories.

   Once the useful patterns are represented in `.ai/skills/**/references`, delete `.snippets` so canonical guidance has one maintained home.

3. Map snippet themes to existing owners.

   FastAPI app lifespan and dependency examples belong under `.ai/skills/fastapi/references`. Async engine/session lifecycle and Docker Compose examples belong under backend or SQLAlchemy/Postgres-owned references depending on current ownership. Celery app and task examples belong under `.ai/skills/celery/references`. General pyproject/Ruff guidance belongs under `.ai/skills/python/references/devex-patterns.md`.

4. Validate with existing surface checks plus focused path checks.

   The implementation should run `python3 scripts/verify_agent_first_surface.py` after edits. If examples add new relative links, the implementation should also verify those links or avoid adding links that require extra verification.

## Risks / Trade-offs

- Snippet-specific imports leak into general guidance -> Adapt examples to placeholders or explain the local assumptions next to the example.
- Reference docs become too long -> Keep examples focused and move only the patterns that clarify current guidance.
- Public skill surface expands accidentally -> Do not create new `.ai/skills/<granular-skill>` packages or compatibility redirects; update only existing owner references.
- Useful snippet content is lost during cleanup -> Complete the snippet-to-reference mapping before deleting `.snippets`, then review the resulting examples against the source themes.
- Validation misses documentation drift -> Run the existing verifier and inspect changed Markdown paths manually.
