## Why

Macwdo skills already encode implementation and review conventions, but there is no dedicated planning agent that selects the right skills before implementation. Adding a planner agent and tightening the reviewer agent prompt makes agent usage more predictable for both "plan this feature" and "review this diff" workflows.

## What Changes

- Add a new `macwdo-planner` skill package with an agent config.
- Document planner behavior for inspecting the request and repo, selecting relevant Macwdo skills, loading their guidance, and producing a decision-complete implementation plan.
- Update Macwdo namespace/router skills so `macwdo-planner` is discoverable.
- Clarify the existing `macwdo-reviewer` agent prompt so it inspects current code, git state, diffs, and relevant Macwdo skills before reporting findings.

## Capabilities

### New Capabilities

- `macwdo-planning-agents`: Planner and reviewer agent behavior for Macwdo skill-guided planning and review.

### Modified Capabilities

None.

## Impact

- Affected skills: `.codex/skills/macwdo-planner`, `.codex/skills/macwdo-reviewer`, `.codex/skills/macwdo`, and `.codex/skills/macwdo-explorer`.
- Affected config: `agents/openai.yaml` files for planner and reviewer agent prompts.
- No runtime dependencies, application APIs, or external systems are changed.
