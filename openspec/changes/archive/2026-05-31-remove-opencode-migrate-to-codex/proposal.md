## Why

The active repository still treats OpenCode as a first-class runtime even though the desired product direction is now Codex-only. That keeps duplicate assets, install paths, and verification logic alive in the codebase and makes documentation and maintenance heavier than necessary.

## What Changes

- **BREAKING** Remove the `.opencode/` runtime asset tree from the packaged product surface.
- **BREAKING** Remove OpenCode-specific installer targets, destination resolution, and list/help output from the Node CLI and shell installer.
- Rewrite active documentation and architecture guidance so they describe only Codex skills, Codex install locations, and Codex-oriented workflows.
- Update package verification so it validates only bundled Codex assets and fails on stale active OpenCode references outside archived history.
- Keep archived OpenSpec history unchanged as historical record.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `mires-namespace-distribution`: Change the package, installer, documentation, and verification requirements from Codex-plus-OpenCode distribution to Codex-only distribution.

## Impact

Affected areas include `lib/mires-cli.js`, `install.sh`, `scripts/verify-package.js`, `package.json`, `README.md`, `docs/mires-skill-architecture.md`, `AGENTS.md`, `opencode.json`, and the active runtime/spec source trees that currently reference `.opencode` assets or OpenCode behavior.
