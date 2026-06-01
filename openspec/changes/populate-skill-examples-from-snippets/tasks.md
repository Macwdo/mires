## 1. Inventory And Mapping

- [x] 1.1 Review `.snippets/python/**` and map each useful example to an existing `.ai/skills/**/references` owner.
- [x] 1.2 Inspect the target reference files before editing and identify which existing sections should receive examples.
- [x] 1.3 Exclude snippets that are too project-specific or duplicate existing guidance without adding clarity.

## 2. Reference Updates

- [x] 2.1 Add adapted FastAPI lifespan, router startup, dependency, and async session examples to the relevant FastAPI references.
- [x] 2.2 Add adapted async SQLAlchemy engine/session lifecycle and database boundary examples to the relevant backend, FastAPI, SQLAlchemy, or Postgres references.
- [x] 2.3 Add adapted service boundary and AWS client construction examples to the relevant backend or Python references.
- [x] 2.4 Add adapted Celery app and task execution examples to the Celery references.
- [x] 2.5 Add adapted Docker Compose and Python tooling examples to the backend and Python DevEx references.
- [x] 2.6 Keep top-level `.ai/skills/*/SKILL.md` files concise unless their reference index needs an update.

## 3. Validation

- [x] 3.1 Remove the `.snippets` tree after useful examples have been migrated into `.ai/skills` references.
- [x] 3.2 Verify every added relative path or reference target exists.
- [x] 3.3 Verify `.snippets` is no longer present as an active repository tree.
- [x] 3.4 Run `python3 scripts/verify_agent_first_surface.py` and resolve any failures.
- [x] 3.5 Run `openspec validate populate-skill-examples-from-snippets --strict` and resolve any failures.
- [x] 3.6 Review `git status --short` to confirm only intended files changed.
