# mires-namespace-distribution Specification

## Purpose
Define how Mires packages and exposes its canonical `.ai` runtime assets, CLI naming, documentation, verification, and public skill namespace.

## Requirements
### Requirement: Duplicate runtime surface is removed
The system SHALL remove committed duplicate runtime assets and export maintenance from active Mires distribution.

#### Scenario: Active repository is inspected
- **WHEN** active repository files are inspected outside archived OpenSpec history
- **THEN** no second runtime/export tree is present
- **AND** active documentation describes `.ai` as the only install, runtime, discovery, and compatibility target

#### Scenario: Verification runs
- **WHEN** maintainers run the documented verification command
- **THEN** it fails if active duplicate runtime assets exist
- **AND** it does not require an export sync check

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
- **THEN** the canonical `.ai/agents` tree includes the requested planner, explorer, tester, researcher, reviewer, project-conventions, backend, Python, FastAPI, Django, LangGraph, frontend, React, Next.js, React Query, React Hook Form, and Zod agents
- **AND** active runtime discovery uses those `.ai/agents` identifiers

#### Scenario: Active runtime assets are `.ai` only
- **WHEN** the package is prepared for distribution
- **THEN** the active runtime asset source consists of the canonical `.ai/agents` and `.ai/skills` trees
- **AND** the package does not provide a second runtime/export tree
- **AND** it does not ship or document a second runtime install surface

#### Scenario: Agent prompts reference Mires skills
- **WHEN** a bundled agent config references local skills in prompts or descriptions
- **THEN** it references active `mires` skill IDs instead of legacy-only skill IDs

#### Scenario: Public runtime discovery favors agents
- **WHEN** Mires runtime assets are discovered
- **THEN** public descriptions and namespace maps emphasize specialized Mires agents and routers
- **AND** granular implementation guidance is absent from the default public catalog and remains in owner-managed references

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, canonical `.ai` assets, and bounded public agent surface without stale legacy runtime references or duplicate runtime behavior in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and canonical `.ai` authoring paths where relevant
- **AND** documentation does not describe a second runtime install surface

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths and canonical `.ai` runtime assets
- **AND** it fails on stale legacy runtime references or duplicate runtime assets in active product files

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship a second runtime surface

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires skills are public agent entrypoints
- **AND** it explains where granular implementation guidance lives in the canonical `.ai` layout

### Requirement: Archived OpenSpec history remains unchanged
The system SHALL preserve archived OpenSpec change history without forcing historical namespace rewrites.

#### Scenario: Archived changes retain historical text
- **WHEN** the namespace rename is implemented
- **THEN** files under `openspec/changes/archive/**` are not rewritten solely to replace historical Macwdo references

### Requirement: Distribution keeps granular guidance behind owner packages
The system SHALL keep useful granular implementation guidance inside canonical `.ai/skills` reference files owned by the relevant public agent or workflow package.

#### Scenario: Existing prompt needs focused implementation detail
- **WHEN** a prompt needs narrow implementation guidance that was formerly surfaced as a standalone granular skill
- **THEN** the guidance is loaded from the owning agent or workflow package references under `.ai/skills`
- **AND** the public routing surface remains agent-first

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent or workflow package that now owns the reference material
