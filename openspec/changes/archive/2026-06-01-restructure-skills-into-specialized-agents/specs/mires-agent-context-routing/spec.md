## ADDED Requirements

### Requirement: Public Mires entrypoints are agent-first
The system SHALL expose a bounded set of public Mires skill entrypoints centered on specialized agents and routing workflows.

#### Scenario: User opens the Mires namespace
- **WHEN** a user or agent loads the `mires` namespace skill
- **THEN** the namespace lists public specialized agents and their domains
- **AND** it does not enumerate every granular implementation guide as a first-class routing target

#### Scenario: User asks for domain-specific work
- **WHEN** a user asks for backend, Django, FastAPI, LangGraph, React, Next.js, testing, review, research, or project-convention work
- **THEN** Mires routes the request to the corresponding specialized agent entrypoint before loading domain-specific implementation details

### Requirement: Specialized agents own granular context loading
Each specialized Mires agent SHALL define the granular local guidance it may load and the conditions for loading that guidance.

#### Scenario: Backend implementation starts
- **WHEN** a backend implementation request is routed through a Mires backend agent
- **THEN** the agent loads project-convention guidance before selecting framework-specific implementation references

#### Scenario: Frontend implementation starts
- **WHEN** a React or Next.js implementation request is routed through a Mires frontend agent
- **THEN** the agent loads only the frontend references needed for the detected framework and requested work

### Requirement: Granular implementation guidance is not default public context
The system SHALL keep granular implementation guidance outside the default public skill surface unless a compatibility redirect is required.

#### Scenario: Granular guidance is retained
- **WHEN** detailed Python, Django, FastAPI, LangGraph, React, Next.js, testing, or DevEx guidance remains useful
- **THEN** it is stored as agent-owned reference material or private support guidance loaded only by the owning agent

#### Scenario: Legacy granular skill ID is invoked
- **WHEN** a user or prompt invokes a legacy granular Mires skill ID that remains for compatibility
- **THEN** the skill provides a concise redirect to the owning specialized agent instead of duplicating the full implementation guide

### Requirement: Routing surface is verified
The project SHALL provide a validation path that detects accidental growth of the public Mires skill surface.

#### Scenario: Verification runs after restructuring
- **WHEN** maintainers run the documented verification command
- **THEN** it reports the public Mires agent entrypoints
- **AND** it fails when the namespace reintroduces a broad granular skill catalog or a redirect stub contains full leaf guidance

#### Scenario: New public agent is added
- **WHEN** maintainers intentionally add a new public Mires agent entrypoint
- **THEN** they update the documented public-entrypoint list and verification expectations in the same change
