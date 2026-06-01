## 1. Global Convention Gate

- [x] 1.1 Add an AI implementation gate section to `AGENTS.md` requiring backend convention discovery before code edits.
- [x] 1.2 Define the required convention report fields: configuration, database/session, dependency injection, service/repository boundaries, error handling, testing, naming, and module organization.
- [x] 1.3 State that current repository conventions override generic Mires examples and external best practices.

## 2. Workflow Skills And Agents

- [x] 2.1 Add a `mires-project-conventions` workflow skill for evidence-based repository convention discovery.
- [x] 2.2 Add a `mires-backend-orchestrator` workflow skill that sequences discovery, skill selection, implementation, validation, and review.
- [x] 2.3 Add a `mires-backend-reviewer` workflow skill that reports convention drift and missing validation.
- [x] 2.4 Add Codex `agents/openai.yaml` metadata for workflow skills that benefit from dedicated subagent invocation.

## 3. Settings And Backend Drift Prevention

- [x] 3.1 Add a `mires-python-settings` skill covering Pydantic Settings, Dynaconf, Django settings, environment-only configuration, and dataclass-settings avoidance.
- [x] 3.2 Update router maps so the new convention, backend, reviewer, and settings skills are discoverable.
- [x] 3.3 Update high-risk backend skills to clarify that source-repo examples are non-authoritative unless they match the current target repository.

## 4. Documentation And Validation

- [x] 4.1 Update `docs/mires-skill-architecture.md` to explain workflow agents, skills, standards, checklists, and the convention-gated backend flow.
- [x] 4.2 Validate that all new skill paths referenced by router maps exist.
- [x] 4.3 Run repository checks appropriate for documentation and packaging changes, including `git status --short` and any available package verification.
