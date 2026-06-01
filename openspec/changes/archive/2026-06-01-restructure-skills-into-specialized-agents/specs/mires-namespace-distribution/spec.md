## MODIFIED Requirements

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active Codex runtime assets using `mires` skill IDs, with public runtime discovery centered on specialized Mires agent entrypoints instead of the full granular support-skill set.

#### Scenario: Codex skills use Mires namespace
- **WHEN** the package includes active Codex skills
- **THEN** every active public skill directory and `SKILL.md` front matter name uses the `mires` namespace

#### Scenario: Active runtime assets are Codex-only
- **WHEN** the package is prepared for distribution
- **THEN** the active runtime asset surface consists of the bundled `.codex/skills/` tree without a second runtime asset tree or slash-command bundle

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references active `mires` skill IDs instead of legacy skill IDs

#### Scenario: Public runtime discovery favors agents
- **WHEN** Codex discovers packaged Mires runtime assets
- **THEN** public descriptions and namespace maps emphasize specialized Mires agents and routers
- **AND** granular implementation guidance is absent from the default public catalog except for concise compatibility redirects

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, Codex runtime assets, and bounded public agent surface without stale legacy runtime references in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and Codex skill locations without describing a second runtime install surface

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the renamed Mires executable paths and bundled Codex runtime assets while failing on stale legacy runtime references in active product files

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship a second runtime surface

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires skills are public agent entrypoints
- **AND** it explains where granular implementation guidance lives after restructuring

## ADDED Requirements

### Requirement: Distribution preserves compatibility redirects
The system SHALL preserve a migration path for existing granular Mires skill IDs that are removed from the public agent surface.

#### Scenario: Existing prompt references old granular skill
- **WHEN** an existing prompt names a granular skill ID that remains in the package for compatibility
- **THEN** the packaged skill redirects to the owning specialized agent using concise guidance
- **AND** it does not include the former full implementation reference content

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent that replaces direct invocation
