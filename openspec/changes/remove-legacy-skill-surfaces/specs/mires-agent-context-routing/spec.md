## MODIFIED Requirements

### Requirement: Retired skill domains have `.ai` ownership
The system SHALL preserve useful Mires behavior from the retired skill corpus under canonical `.ai` agents or owner-loaded references before removing duplicate runtime assets. Legacy skill packages, compatibility redirects, and public granular skill IDs MUST NOT remain active when their behavior can be represented by an existing specialized agent or workflow-owned reference.

#### Scenario: Retired skill maps to routing domain
- **WHEN** a retired Mires skill represents a meaningful routing domain such as backend, Django, FastAPI, LangGraph, React, Next.js, testing, research, review, or project conventions
- **THEN** the domain has a corresponding public or nested `AGENT.md` under `.ai/agents`
- **AND** the agent has matching runtime metadata under `agents/openai.yaml`
- **AND** no active legacy skill package remains as a competing public route for the same domain

#### Scenario: Retired skill maps to implementation reference
- **WHEN** a retired Mires skill represents focused implementation guidance below a routing domain
- **THEN** the full useful guidance is stored as a reference owned by the nearest specialized `.ai` domain
- **AND** the public route for that guidance is the canonical agent or owner workflow package
- **AND** the retired skill package or compatibility redirect is removed from active source

#### Scenario: Retired skill has no useful remaining guidance
- **WHEN** a retired Mires skill is obsolete, duplicated, or fully represented by existing agent instructions
- **THEN** the retired skill is removed from active source
- **AND** no placeholder compatibility package is retained solely for old skill discovery

### Requirement: Granular implementation guidance is not default public context
The system SHALL keep granular implementation guidance outside the default public routing surface and store it as agent-owned or workflow-owned references. Retained granular guidance MUST have an explicit active owner and MUST NOT be exposed as a standalone legacy skill package or compatibility redirect when owner-loaded reference material is sufficient.

#### Scenario: Granular guidance is retained
- **WHEN** detailed Python, Django, FastAPI, LangGraph, React, Next.js, testing, or DevEx guidance remains useful
- **THEN** it is stored as agent-owned reference material or private support guidance loaded only by the owning agent
- **AND** its canonical source path is under `.ai/skills/<owner>/references/`
- **AND** the owner package or agent documents when that reference may be loaded

#### Scenario: Granular legacy invocation is encountered
- **WHEN** active prompts, docs, or runtime metadata reference an old granular skill ID whose guidance is now an owner-loaded reference
- **THEN** the active file is updated to invoke the owning Mires agent or workflow package instead
- **AND** no active compatibility redirect is introduced for that old granular skill ID

### Requirement: Routing surface is verified
The project SHALL provide a validation path that detects accidental growth of the public Mires agent surface, missing migrated domain ownership, stale legacy skill IDs, orphaned references, and reintroduction of duplicate runtime assets.

#### Scenario: Verification runs after restructuring
- **WHEN** maintainers run the documented verification command
- **THEN** it reports the public Mires agent entrypoints from `.ai/agents`
- **AND** it fails when the namespace reintroduces a broad granular skill catalog or an unexpected granular skill package reappears
- **AND** it fails when useful retired Mires skill behavior has no canonical `.ai` owner
- **AND** it fails when active duplicate runtime assets are present
- **AND** it fails when active compatibility redirects preserve legacy granular skill IDs that have owner-loaded references
- **AND** it fails when reference files under `.ai/skills/**/references/` are not documented by an owning `SKILL.md`, `AGENT.md`, or explicit verification allowlist

#### Scenario: New public agent is added
- **WHEN** maintainers intentionally add a new public Mires agent entrypoint
- **THEN** they update the documented public-entrypoint list and verification expectations in the same change
- **AND** they add the canonical agent source under `.ai/agents`
