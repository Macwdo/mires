## Why

The project currently installs only Codex assets from `.codex/skills`, while this repository also contains OpenCode assets under `.opencode/skills` and `.opencode/commands`. Users who want one package and one installer flow for both agent runtimes still have to copy OpenCode files manually, which makes the public package incomplete.

## What Changes

- Extend the npm package allowlist so the published package includes the supported OpenCode assets alongside the existing Codex skills.
- Expand the Node CLI installer to support explicit installation targets for Codex, OpenCode, or both.
- Expand the shell installer with matching target selection and destination handling.
- Install OpenCode skills and slash commands into user-level and project-level OpenCode locations without packaging transient `.opencode` workspace files.
- Update verification and documentation so packaged contents and installer behavior are validated for both runtimes.

## Capabilities

### New Capabilities
- `codex-opencode-installer`: Defines packaging and installation behavior for Codex skills plus OpenCode skills and commands from one Macwdo distribution.

### Modified Capabilities

- None.

## Impact

- Affects `package.json`, `README.md`, `lib/macwdo-cli.js`, `install.sh`, and `scripts/verify-package.js`.
- Adds new packaged asset coverage for `.opencode/skills/**` and `.opencode/commands/**` while excluding local dependency and lockfile noise.
- Changes CLI and shell installer help text, flags, destination resolution, and verification flows.
