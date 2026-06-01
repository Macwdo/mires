## ADDED Requirements

### Requirement: Mires npm package exposes Mires CLI
The system SHALL provide a publishable npm package named `@mires/mires` that exposes a `mires` executable command.

#### Scenario: Global npm install links Mires command
- **WHEN** a user installs the package with `npm install -g @mires/mires`
- **THEN** npm links the package executable as `mires`

#### Scenario: Mires CLI reports version
- **WHEN** a user runs `mires --version`
- **THEN** the CLI prints the package version from the installed package metadata

#### Scenario: Mires CLI reports help
- **WHEN** a user runs `mires --help`
- **THEN** the CLI prints available commands and install scope options using Mires naming

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active Codex and OpenCode runtime assets using `mires` skill and command names.

#### Scenario: Codex skills use Mires namespace
- **WHEN** the package includes active Codex skills
- **THEN** every formerly Macwdo skill directory and `SKILL.md` front matter name is renamed to the equivalent `mires` name

#### Scenario: OpenCode entrypoints use Mires namespace
- **WHEN** the package includes OpenCode skills and commands
- **THEN** the reviewer and tester OpenCode skill and command entrypoints use `mires-reviewer` and `mires-tester`

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references the renamed `mires` skill IDs instead of `macwdo` skill IDs

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, and runtime asset names without stale Macwdo product-source references.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@mires/mires`, `mires`, and `mires-*` names

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the renamed Mires executable paths and bundled Mires runtime assets

#### Scenario: Active product source has no stale Macwdo namespace references
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no `macwdo`, `Macwdo`, or `@macwdo` namespace references remain

### Requirement: Archived OpenSpec history remains unchanged
The system SHALL preserve archived OpenSpec change history without forcing historical namespace rewrites.

#### Scenario: Archived changes retain historical text
- **WHEN** the namespace rename is implemented
- **THEN** files under `openspec/changes/archive/**` are not rewritten solely to replace historical Macwdo references
