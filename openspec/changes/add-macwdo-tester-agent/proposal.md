## Why

Macwdo agent testing is currently split across several `macwdo-agent-testing-*` skills, while the practical workflow also depends on the separate `agent-browser` and `portless` skills. A single `macwdo-tester` agent will make local app verification easier to invoke and harder to run incorrectly.

## What Changes

- Add a new `macwdo-tester` skill and agent configuration as the canonical testing entrypoint.
- Consolidate the existing portless launch, browser verification, and reporting guidance into the `macwdo-tester` workflow.
- Compose `macwdo-tester` with the existing personal `agent-browser` and `portless` skills instead of duplicating their full CLI references.
- Update Macwdo routers so agent testing points to `macwdo-tester`.
- Retire or de-emphasize the old `macwdo-agent-testing-*` agent entrypoints after the consolidated agent exists.

## Capabilities

### New Capabilities

- `macwdo-tester-agent`: Defines the unified Macwdo testing agent behavior, including worktree validation, portless launch, browser verification, and concise result reporting.

### Modified Capabilities

- None.

## Impact

- Affected skill files under `.codex/skills/`, especially the current `macwdo-agent-testing-*` family.
- New `.codex/skills/macwdo-tester/SKILL.md` and `.codex/skills/macwdo-tester/agents/openai.yaml`.
- Router updates in `.codex/skills/macwdo/SKILL.md` and `.codex/skills/macwdo-explorer/SKILL.md`.
- Possible removal or compatibility treatment for old agent-testing agent configs.
