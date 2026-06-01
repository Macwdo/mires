## Why

The project has moved from the Macwdo npm organization and namespace to Mires. The repository still exposes Macwdo package names, CLI commands, skill IDs, OpenCode commands, agent prompts, and documentation, which would publish and install the wrong branded runtime assets.

## What Changes

- **BREAKING** Rename the npm package from `@macwdo/macwdo` to `@mires/mires`.
- **BREAKING** Rename the CLI command from `macwdo` to `mires` and update executable source paths accordingly.
- **BREAKING** Rename active Codex skill packages from `macwdo*` to `mires*`, including front matter names and cross-skill references.
- **BREAKING** Rename active OpenCode skill and slash command entrypoints from `macwdo-*` to `mires-*`.
- Update agent display names, descriptions, default prompts, installer verification, README usage, and architecture documentation to use Mires naming.
- Preserve archived OpenSpec change history without rewriting historical `macwdo` references.

## Capabilities

### New Capabilities

- `mires-namespace-distribution`: Defines the Mires package, CLI, runtime skill namespace, OpenCode entrypoints, and documentation expectations after the namespace rename.

### Modified Capabilities

- None.

## Impact

- Affects package metadata, npm publish/install examples, CLI executable names, CLI implementation files, installer verification scripts, root documentation, architecture documentation, active Codex skill directories, active OpenCode skill directories, active OpenCode command files, and agent config prompts.
- Existing users of `@macwdo/macwdo`, `macwdo`, or `macwdo-*` skill IDs must switch to `@mires/mires`, `mires`, and `mires-*` names.
- Archived OpenSpec artifacts remain historical records and are intentionally excluded from the active rename sweep.
