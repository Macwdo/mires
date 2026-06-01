## MODIFIED Requirements

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active runtime assets using `mires` identifiers, with public runtime discovery centered on specialized Mires agent entrypoints from the canonical `.ai/agents` and `.ai/skills` layout instead of the full granular support-skill set.

#### Scenario: Canonical assets use Mires namespace
- **WHEN** the repository includes active Mires agents and skills
- **THEN** every canonical public agent and skill identifier uses the `mires` namespace

#### Scenario: Canonical assets include requested hierarchy
- **WHEN** the repository prepares active runtime assets
- **THEN** the canonical `.ai/agents` tree includes the requested planner, explorer, tester, researcher, backend, Python, FastAPI, Django, frontend, React, React Query, React Hook Form, and Zod agents
- **AND** packaged compatibility exports preserve those identifiers for Codex discovery where supported

#### Scenario: Active runtime assets are Codex compatible
- **WHEN** the package is prepared for distribution
- **THEN** the active runtime asset source consists of the canonical `.ai/agents` and `.ai/skills` trees
- **AND** the package provides a Codex-compatible `.codex/skills` export
- **AND** it does not ship or document a second non-Codex runtime install surface

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references active `mires` skill IDs instead of legacy skill IDs

#### Scenario: Public runtime discovery favors agents
- **WHEN** Codex discovers packaged Mires runtime assets
- **THEN** public descriptions and namespace maps emphasize specialized Mires agents and routers
- **AND** granular implementation guidance is absent from the default public catalog except for concise compatibility redirects

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, canonical `.ai` assets, Codex-compatible exports, and bounded public agent surface without stale legacy runtime references in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, canonical `.ai` authoring paths, and Codex compatibility export paths where relevant
- **AND** documentation does not describe a second runtime install surface

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths, canonical `.ai` runtime assets, and bundled Codex-compatible exports
- **AND** it fails on stale legacy runtime references in active product files

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship a second runtime surface
- **AND** `.codex/skills` is described only as a Codex compatibility export from `.ai`

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires assets are public agent entrypoints
- **AND** it explains where granular implementation guidance lives in the canonical `.ai` layout
- **AND** it explains how Codex-compatible skill packages are exported

### Requirement: Distribution preserves compatibility redirects
The system SHALL preserve a migration path for existing granular Mires skill IDs that are removed from the public agent surface.

#### Scenario: Existing prompt references old granular skill
- **WHEN** an existing prompt names a granular skill ID that remains in the package for compatibility
- **THEN** the packaged skill redirects to the owning specialized agent using concise guidance
- **AND** it does not include the former full implementation reference content
- **AND** the canonical redirect source is stored under `.ai/skills`

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent that replaces direct invocation
