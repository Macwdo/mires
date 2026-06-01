---
name: project-conventions
description: Repository convention discovery workflow to inspect existing patterns before backend or framework-specific implementation.
---

# Project Conventions

## When To Use

Use before backend implementation or any work where the local architecture pattern must be discovered first.

## Core Rules

- Inspect the repository before proposing patterns.
- Record findings with evidence paths.
- Mark unclear conventions explicitly.
- Do not edit code while gathering conventions.

## Preferred Patterns

- Short convention reports with direct file evidence.
- Conservative choices when the repo has no clear precedent.

## Anti-Patterns

- Inventing architecture because the repo is unfamiliar.
- Replacing evidence with generic best-practice claims.
- Skipping testing or dependency patterns when they are relevant to the task.

## Checklist

- Inspect repo docs and configs.
- Inspect nearby implementation files.
- Capture configuration, database, dependency, service, error, testing, and naming conventions.
- Record uncertainties explicitly.

## References Index

- `references/repository-discovery-checklist.md`
