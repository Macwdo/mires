## ADDED Requirements

### Requirement: Codex runtime surface is removed
The system SHALL remove committed Codex runtime assets and Codex export maintenance from active Mires distribution.

#### Scenario: Active repository is inspected
- **WHEN** active repository files are inspected outside archived OpenSpec history
- **THEN** no `.codex/skills` runtime tree is present
- **AND** active documentation does not describe Codex as an install, runtime, discovery, or compatibility target

#### Scenario: Verification runs
- **WHEN** maintainers run the documented verification command
- **THEN** it fails if active `.codex` runtime assets exist
- **AND** it does not require a Codex export sync check

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
- **THEN** the CLI prints available commands and `.ai`-oriented installation information using Mires naming

#### Scenario: Install flow does not require runtime target selection
- **WHEN** a user runs `mires install`
- **THEN** the CLI plans installation for bundled `.ai` agents and skills without requiring runtime target selection

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active runtime assets using `mires` skill IDs, with public runtime discovery centered on specialized Mires agent entrypoints from the canonical `.ai/agents` and `.ai/skills` layout instead of the full granular support-skill set.

#### Scenario: Canonical assets use Mires namespace
- **WHEN** the repository includes active Mires agents and skills
- **THEN** every canonical public agent and skill identifier uses the `mires` namespace

#### Scenario: Canonical assets include requested hierarchy
- **WHEN** the repository prepares active runtime assets
- **THEN** the canonical `.ai/agents` tree includes the requested planner, explorer, tester, researcher, backend, Python, FastAPI, Django, LangGraph, frontend, React, Next.js, React Query, React Hook Form, and Zod agents
- **AND** active runtime discovery uses those `.ai/agents` identifiers

#### Scenario: Active runtime assets are `.ai` only
- **WHEN** the package is prepared for distribution
- **THEN** the active runtime asset source consists of the canonical `.ai/agents` and `.ai/skills` trees
- **AND** the package does not provide a `.codex/skills` export
- **AND** it does not ship or document a Codex runtime install surface

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references active `mires` skill IDs instead of legacy or Codex-only skill IDs

#### Scenario: Public runtime discovery favors agents
- **WHEN** Mires runtime assets are discovered
- **THEN** public descriptions and namespace maps emphasize specialized Mires agents and routers
- **AND** granular implementation guidance is absent from the default public catalog except for concise `.ai/skills` redirects

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, canonical `.ai` assets, and bounded public agent surface without stale legacy runtime references or Codex runtime behavior in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and canonical `.ai` authoring paths where relevant
- **AND** documentation does not describe a Codex runtime install surface

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths and canonical `.ai` runtime assets
- **AND** it fails on stale legacy runtime references or Codex runtime assets in active product files

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship a Codex runtime surface

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires skills are public agent entrypoints
- **AND** it explains where granular implementation guidance lives in the canonical `.ai` layout

### Requirement: Distribution preserves `.ai` redirects only
The system SHALL preserve a migration path for useful existing granular Mires skill IDs only inside canonical `.ai/skills`.

#### Scenario: Existing prompt references old granular skill
- **WHEN** an existing prompt names a granular skill ID that remains in `.ai/skills`
- **THEN** the skill redirects to the owning specialized agent using concise guidance
- **AND** it does not include the former full implementation reference content
- **AND** the canonical redirect source is stored under `.ai/skills`

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent that replaces direct invocation
