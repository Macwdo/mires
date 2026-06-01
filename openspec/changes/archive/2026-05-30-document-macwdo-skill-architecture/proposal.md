## Why

The `.codex/skills/macwdo/` namespace is already a large structured knowledge base for how Macwdo implements projects, but its architecture is only implicit in the skill files themselves. A concise architecture guide will make it easier to understand how the project is organized, judge whether the current structure is effective, and evolve the skills without adding accidental duplication or routing drift.

## What Changes

- Add documentation that explains the repository's skill distribution model across `.codex/skills`, `.opencode/skills`, `.opencode/commands`, and `openspec/changes`.
- Document how the Macwdo skill hierarchy is intended to work: namespace entrypoint, explorer/router skills, leaf implementation skills, review/planning/testing workflows, and agent configs.
- Add an evaluation framework for deciding whether a skill belongs as a router, a leaf, a runtime command, or an agent-backed workflow.
- Add concrete recommendations for maintaining the structure as the skill library grows.
- No runtime behavior, installer behavior, or skill invocation behavior changes are introduced by this change.

## Capabilities

### New Capabilities

- `macwdo-skill-architecture-guide`: Defines the expected documentation and evaluation support for understanding and maintaining the Macwdo skill architecture.

### Modified Capabilities

None.

## Impact

- Adds project documentation for the Macwdo skill architecture.
- Adds an OpenSpec capability spec covering the architecture guide expectations.
- Affects Markdown documentation only.
- No new dependencies, commands, generated code, package metadata, or installer destination changes.
