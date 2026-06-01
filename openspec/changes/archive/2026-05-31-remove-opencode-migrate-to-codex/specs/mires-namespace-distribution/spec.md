## MODIFIED Requirements

### Requirement: Mires npm package exposes Mires CLI
The system SHALL provide a publishable npm package named `@macwdo/mires` that exposes a `mires` executable command.

#### Scenario: Global npm install links Mires command
- **WHEN** a user installs the package with `npm install -g @macwdo/mires`
- **THEN** npm links the package executable as `mires`

#### Scenario: Mires CLI reports version
- **WHEN** a user runs `mires --version`
- **THEN** the CLI prints the package version from the installed package metadata

#### Scenario: Mires CLI reports help
- **WHEN** a user runs `mires --help`
- **THEN** the CLI prints available commands and Codex-oriented install scope options using Mires naming

#### Scenario: Install flow does not require runtime target selection
- **WHEN** a user runs `mires install`
- **THEN** the CLI plans installation for bundled Codex skills without requiring or advertising OpenCode runtime targets

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active Codex runtime assets using `mires` skill IDs and agent references.

#### Scenario: Codex skills use Mires namespace
- **WHEN** the package includes active Codex skills
- **THEN** every formerly Macwdo skill directory and `SKILL.md` front matter name is renamed to the equivalent `mires` name

#### Scenario: Active product source contains no OpenCode runtime assets
- **WHEN** active repository files are inspected outside `openspec/changes/archive/**`
- **THEN** no active `.opencode/` runtime asset directories, OpenCode command files, or OpenCode-only product config files remain

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references the active `mires` skill IDs instead of legacy or OpenCode-specific runtime names

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, and Codex runtime assets without stale active OpenCode product references.

#### Scenario: Documentation shows Codex install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and Codex skill locations without describing OpenCode install paths or commands

#### Scenario: Package verification checks Codex paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths and bundled Codex runtime assets while failing on stale active OpenCode product-source references

#### Scenario: Active product source has no stale OpenCode references
- **WHEN** active repository files are searched outside `openspec/changes/archive/**`
- **THEN** no active product-source references to `.opencode`, `opencode`, or `OpenCode` remain
