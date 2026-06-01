## Why

`macwdo-tester` and `macwdo-reviewer` already exist as Codex skill packages with agent configs, but there are no matching OpenCode skills or slash commands. The package can now install assets for either runtime, so these two high-value entrypoints should be available consistently in Codex and OpenCode.

## What Changes

- Add OpenCode skill packages for `macwdo-tester` and `macwdo-reviewer`.
- Add OpenCode slash commands for `macwdo-tester` and `macwdo-reviewer` so users can invoke those workflows directly.
- Keep the detailed workflow guidance in the skill files and make the slash commands thin entrypoints that route to the corresponding skills.
- Update package verification and documentation so the new OpenCode assets are bundled, listed, and installable through the existing `codex|opencode|both` installer targets.

## Capabilities

### New Capabilities

- `macwdo-cross-runtime-subagents`: Defines how Macwdo tester and reviewer entrypoints are packaged and exposed across Codex and OpenCode.

### Modified Capabilities

None.

## Impact

- New files under `.opencode/skills/macwdo-tester/`, `.opencode/skills/macwdo-reviewer/`, and `.opencode/commands/`.
- README updates for the new OpenCode commands and runtime parity expectations.
- Package verification updates only if the current checks do not already assert the new assets.
- No new runtime dependencies or installer flags.
