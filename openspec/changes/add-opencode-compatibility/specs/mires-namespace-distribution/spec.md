## ADDED Requirements

### Requirement: Mires supports OpenCode compatibility output
The system SHALL validate and install OpenCode-compatible runtime assets generated from canonical `.ai/agents` and `.ai/skills` source assets.

#### Scenario: OpenCode compatibility check runs
- **WHEN** a maintainer runs the compatibility check with target `opencode`
- **THEN** the check validates canonical `.ai` agents and skills for OpenCode generation
- **AND** it reports success without requiring Codex-specific install output

#### Scenario: OpenCode install runs
- **WHEN** a user runs the compatibility installer with target `opencode`
- **THEN** generated OpenCode agent definitions are written under the configured OpenCode home
- **AND** generated OpenCode skill packages are written to an OpenCode-discoverable skill directory
- **AND** the installed files reference generated paths instead of repository-local `.ai` paths

#### Scenario: OpenCode dry run runs
- **WHEN** a user runs the OpenCode installer in dry-run mode
- **THEN** the command reports the OpenCode files it would create or refresh
- **AND** it does not write the OpenCode home directory

### Requirement: Compatibility target selection supports Codex and OpenCode
The system SHALL expose both `codex` and `opencode` as supported compatibility targets without changing the canonical `.ai` asset source.

#### Scenario: Supported target is selected
- **WHEN** a user runs compatibility validation or installation for `codex` or `opencode`
- **THEN** the command dispatches to the matching runtime adapter
- **AND** target-specific validation and generated output are applied only for that runtime

#### Scenario: Unsupported target is selected
- **WHEN** a user runs compatibility validation or installation for an unsupported target
- **THEN** the command fails with a clear unsupported target error
- **AND** no generated runtime files are written

## MODIFIED Requirements

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, canonical `.ai` assets, supported compatibility targets, and bounded public agent surface without stale legacy runtime references or duplicate runtime source behavior in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and canonical `.ai` authoring paths where relevant
- **AND** documentation describes Codex and OpenCode as supported generated compatibility targets
- **AND** documentation does not describe a second runtime authoring source tree

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths, canonical `.ai` runtime assets, and supported Codex and OpenCode compatibility checks
- **AND** it fails on stale legacy runtime references or duplicate runtime source assets in active product files

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship an unsupported duplicate runtime source surface
- **AND** intentional Codex and OpenCode compatibility adapters, tests, and documentation are allowed

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires skills are public agent entrypoints
- **AND** it explains where granular implementation guidance lives in the canonical `.ai` layout
