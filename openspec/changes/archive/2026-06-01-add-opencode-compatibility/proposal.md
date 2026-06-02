## Why

Mires currently validates and installs its canonical `.ai` assets for Codex only, even though the project should support OpenCode users without creating a second source tree. Adding OpenCode compatibility lets the same agent-first `.ai` assets work across both runtimes while preserving the repository's runtime-agnostic authoring model.

## What Changes

- Add OpenCode as a supported compatibility target for validation and installation.
- Generate OpenCode-compatible agent and skill output from the canonical `.ai/agents` and `.ai/skills` trees.
- Update CLI options, documentation, verification, and tests so `codex` and `opencode` are both supported targets.
- Preserve `.ai` as the only canonical authoring layout; OpenCode output is generated runtime state, not committed source.

## Capabilities

### New Capabilities

### Modified Capabilities
- `mires-namespace-distribution`: Extend runtime compatibility requirements from Codex-only generated output to both Codex and OpenCode generated output while keeping `.ai` canonical.

## Impact

- Affected code: `src/main.py`, `src/compatibility/`, installer tests, verification scripts, and documentation.
- Affected runtime systems: Codex remains supported; OpenCode becomes a supported generated installation target.
- No breaking changes are expected for existing Codex validation or install behavior.
