---
name: mires-backend-reviewer
description: "Review backend changes for convention drift. Use after backend implementation or during code review for configuration, database/session, dependency injection, services, repositories, errors, tests, and module organization."
---

# Backend Reviewer

Use this workflow as a review gate after backend implementation. Lead with findings and cite files or diff lines when possible.

## Review Inputs

- The convention report from `project-conventions`.
- The relevant Mires implementation skills used by the change.
- The git diff, touched files, and validation output.

## Checklist

- Configuration follows the existing settings pattern.
- No dataclass settings were introduced when the project uses Pydantic Settings, Dynaconf, Django settings, or another settings system.
- Database engines, session factories, request dependencies, Django initialization, and migrations reuse existing abstractions.
- Sync versus async database style matches the project.
- Dependency injection follows existing framework dependencies, explicit parameters, provider modules, or constructor patterns.
- Service and repository boundaries match the repository.
- Error handling follows existing exception, HTTP error, result, logging, and failure-translation patterns.
- Tests match existing framework, fixtures, naming, database setup, and fake/mock style.
- Naming, imports, helper placement, and module layout match nearby code.
- Any unclear convention is reported rather than hidden behind an assumption.

## Findings

Flag a finding when a change introduces a new configuration, database, session, dependency-injection, service, repository, or testing abstraction without evidence that no existing convention applies.

## Output

1. Findings ordered by severity.
2. Open questions or assumptions that affect correctness.
3. Test gaps or validation notes.
4. Brief summary only after findings.
