## MODIFIED Requirements

### Requirement: Mires runtime assets use Mires skill IDs
The system SHALL package active runtime assets using `mires` agent and workflow identifiers, with public runtime discovery centered on specialized Mires agent entrypoints from the canonical `.ai/agents` and `.ai/skills` layout instead of the full granular support-skill set. Legacy granular skill IDs MUST NOT remain active as public compatibility packages when their content is owned by a specialized agent or workflow reference.

#### Scenario: Canonical assets use Mires namespace
- **WHEN** the repository includes active Mires agents and skills
- **THEN** every canonical public agent and skill identifier uses the `mires` namespace
- **AND** no legacy granular skill ID is retained as an active compatibility surface solely for discovery

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
- **THEN** it references active `mires` agent or workflow identifiers instead of legacy-only skill IDs
- **AND** it does not route directly to owner-loaded reference files as public skills

#### Scenario: Public runtime discovery favors agents
- **WHEN** Mires runtime assets are discovered
- **THEN** public descriptions and namespace maps emphasize specialized Mires agents and routers
- **AND** granular implementation guidance is absent from the default public catalog and remains in owner-managed references
- **AND** compatibility redirects for removed granular skill IDs are absent from active distribution

### Requirement: Mires documentation and verification are consistent
The system SHALL document and verify the Mires package, CLI, canonical `.ai` assets, and bounded public agent surface without stale legacy runtime references, orphaned references, duplicate runtime behavior, or active compatibility skill packages in active product files.

#### Scenario: Documentation shows Mires install commands
- **WHEN** a user reads active documentation
- **THEN** install examples use `@macwdo/mires`, `mires`, and canonical `.ai` authoring paths where relevant
- **AND** documentation does not describe a second runtime install surface

#### Scenario: Package verification checks Mires paths
- **WHEN** maintainers run package verification
- **THEN** it checks the Mires executable paths and canonical `.ai` runtime assets
- **AND** it fails on stale legacy runtime references or duplicate runtime assets in active product files
- **AND** it fails on active compatibility packages for granular skill IDs whose guidance is now owner-loaded reference material
- **AND** it fails on retained reference files without a documented owner

#### Scenario: Active product source has no stale legacy runtime behavior
- **WHEN** active repository files are searched outside `openspec/changes/**`
- **THEN** no active documentation, installer behavior, or bundled assets describe or ship a second runtime surface
- **AND** no active documentation, installer behavior, or bundled assets expose removed granular legacy skills as public routes

#### Scenario: Documentation explains agent-first context loading
- **WHEN** maintainers read the active Mires skill architecture documentation
- **THEN** it explains which Mires skills are public agent entrypoints
- **AND** it explains where granular implementation guidance lives in the canonical `.ai` layout
- **AND** it identifies the owning agent or workflow package for retained legacy-derived reference material

### Requirement: Distribution keeps granular guidance behind owner packages
The system SHALL keep useful granular implementation guidance inside canonical `.ai/skills` reference files owned by the relevant public agent or workflow package, and SHALL remove any active legacy skill package once that guidance has an owner.

#### Scenario: Existing prompt needs focused implementation detail
- **WHEN** a prompt needs narrow implementation guidance that was formerly surfaced as a standalone granular skill
- **THEN** the guidance is loaded from the owning agent or workflow package references under `.ai/skills`
- **AND** the public routing surface remains agent-first
- **AND** the prompt invokes the owner instead of the old granular skill ID

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent or workflow package that now owns the reference material
- **AND** the granular skill package and compatibility redirect are absent from active distribution

#### Scenario: Granular skill has no retained reference
- **WHEN** maintainers determine a granular legacy skill is obsolete or fully duplicated
- **THEN** the skill is removed without creating a replacement reference
- **AND** verification continues to pass because no active prompt, agent, skill, or documentation file refers to it
