## Why

The repository should stop carrying two runtime surfaces. Mires should keep `.ai` as the only active agent and skill authoring layout, with OpenSpec documenting the migration and no committed Codex compatibility tree.

## What Changes

- Use the existing `.codex/skills` content only as migration input, then remove the `.codex` runtime/export surface from active files.
- Populate and verify `.ai/agents` so every meaningful Mires domain formerly discoverable through Codex skills is represented by the right public or nested agent.
- Move routing, delegation, runtime metadata, and implementation guidance into canonical `.ai/agents` and `.ai/skills` assets.
- Remove Codex compatibility export behavior, including `.codex/skills` output, Codex sync checks, and documentation that describes Codex as an install/runtime target.
- Update documentation and verification so active Mires behavior is `.ai`-only.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `mires-agent-context-routing`: Require the `.ai/agents` hierarchy to fully replace direct Codex skill discovery for Mires routing and delegation.
- `mires-namespace-distribution`: Remove Codex compatibility export requirements and require `.ai` to be the only active runtime asset surface.

## Impact

- Affects `.ai/agents/**/AGENT.md`, `.ai/agents/**/agents/openai.yaml`, `.ai/skills/**/SKILL.md`, and `.ai/skills/**/references/**`.
- Removes `.codex/skills/**` and Codex export/sync maintenance from active repository behavior.
- Affects `docs/mires-agent-architecture.md`, `.ai/skills/mires/SKILL.md`, repository guidance, and verification scripts.
- No external API or runtime dependency changes are expected.
