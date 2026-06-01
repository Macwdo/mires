# mires-agent-context-routing Specification

## Purpose
Define how Mires exposes a bounded public set of specialized agent entrypoints from the canonical `.ai/agents` hierarchy while keeping granular implementation guidance behind domain-selected `.ai/skills` references.

## Requirements
### Requirement: Retired skill domains have `.ai` ownership
The system SHALL preserve useful Mires behavior from the retired skill corpus under canonical `.ai` agents, skills, or references before removing duplicate runtime assets.

#### Scenario: Retired skill maps to routing domain
- **WHEN** a retired Mires skill represents a meaningful routing domain such as backend, Django, FastAPI, LangGraph, React, Next.js, testing, research, review, or project conventions
- **THEN** the domain has a corresponding public or nested `AGENT.md` under `.ai/agents`
- **AND** the agent has matching runtime metadata under `agents/openai.yaml`

#### Scenario: Retired skill maps to implementation reference
- **WHEN** a retired Mires skill represents focused implementation guidance below a routing domain
- **THEN** the full guidance is stored as a reference owned by the nearest specialized `.ai` domain
- **AND** the public route for that guidance is the canonical agent or owner skill package

### Requirement: Public Mires entrypoints are agent-first
The system SHALL expose a bounded set of public Mires agent entrypoints centered on specialized agents and routing workflows, with canonical public agent definitions stored under the requested `.ai/agents` hierarchy.

#### Scenario: User opens the Mires namespace
- **WHEN** a user or agent loads the `mires` namespace skill
- **THEN** the namespace lists public specialized agents and their domains
- **AND** it does not enumerate every granular implementation guide as a first-class routing target

#### Scenario: User asks for domain-specific work
- **WHEN** a user asks for backend, Django, FastAPI, LangGraph, React, Next.js, testing, review, research, or project-convention work
- **THEN** Mires routes the request to the corresponding specialized agent entrypoint before loading domain-specific implementation details
- **AND** the canonical public agent source resolves from `.ai/agents/<agent-name>/`
- **AND** routing does not require a second runtime asset tree

#### Scenario: User asks for backend work
- **WHEN** a user asks for Python, FastAPI, Django, SQLAlchemy, AWS, TDD, Celery, Celery Beat, class-based, function-based, or backend pattern work
- **THEN** Mires routes the request through `.ai/agents/mires-backend`
- **AND** it selects the most specific nested Python, FastAPI, Django, or LangGraph subagent for the task

#### Scenario: User asks for frontend work
- **WHEN** a user asks for React, Next.js, React Query, React Hook Form, or Zod work
- **THEN** Mires routes the request through `.ai/agents/mires-frontend`
- **AND** it selects the relevant frontend owner package references for React, Next.js, or TypeScript work

### Requirement: Specialized agents own granular context loading
Each specialized Mires agent SHALL define the granular local guidance it may load and the conditions for loading that guidance from canonical `.ai/skills` references.

#### Scenario: Backend implementation starts
- **WHEN** a backend implementation request is routed through a Mires backend agent
- **THEN** the agent loads project-convention guidance before selecting framework-specific implementation references
- **AND** selected implementation references resolve from the owning `.ai/skills` package
- **AND** selected nested backend subagents remain responsible for their own focused guidance

#### Scenario: Frontend implementation starts
- **WHEN** a React or Next.js implementation request is routed through a Mires frontend agent
- **THEN** the agent loads only the frontend references needed for the detected framework and requested work
- **AND** selected implementation references resolve from the owning `.ai/skills` package

#### Scenario: Explorer runs repository analysis
- **WHEN** `mires-explorer` is used to inspect a repository
- **THEN** it identifies applicable domains from the `.ai/agents` hierarchy
- **AND** it calls or consults the relevant domain subagents to find bugs, errors, and risks

#### Scenario: Tester validates behavior
- **WHEN** `mires-tester` is used to validate whether work is functioning
- **THEN** it calls or consults `mires-explorer` to check for bugs or issues
- **AND** it delegates browser-based verification to `mires-tester-agent-browser` when a browser is required
- **AND** it delegates non-server or portless checks to `mires-tester-portless` when a running port is not needed

#### Scenario: Researcher gathers implementation references
- **WHEN** `mires-researcher` needs current or external implementation references
- **THEN** it uses available MCPs or WebSearch to research the internet
- **AND** it returns sourced references that inform the implementation guidance

### Requirement: Granular implementation guidance is not default public context
The system SHALL keep granular implementation guidance outside the default public routing surface and store it as agent-owned or workflow-owned references.

#### Scenario: Granular guidance is retained
- **WHEN** detailed Python, Django, FastAPI, LangGraph, React, Next.js, testing, or DevEx guidance remains useful
- **THEN** it is stored as agent-owned reference material or private support guidance loaded only by the owning agent
- **AND** its canonical source path is under `.ai/skills`

### Requirement: Routing surface is verified
The project SHALL provide a validation path that detects accidental growth of the public Mires agent surface, missing migrated domain ownership, and reintroduction of duplicate runtime assets.

#### Scenario: Verification runs after restructuring
- **WHEN** maintainers run the documented verification command
- **THEN** it reports the public Mires agent entrypoints from `.ai/agents`
- **AND** it fails when the namespace reintroduces a broad granular skill catalog or an unexpected granular skill package reappears
- **AND** it fails when useful retired Mires skill behavior has no canonical `.ai` owner
- **AND** it fails when active duplicate runtime assets are present

#### Scenario: New public agent is added
- **WHEN** maintainers intentionally add a new public Mires agent entrypoint
- **THEN** they update the documented public-entrypoint list and verification expectations in the same change
- **AND** they add the canonical agent source under `.ai/agents`
