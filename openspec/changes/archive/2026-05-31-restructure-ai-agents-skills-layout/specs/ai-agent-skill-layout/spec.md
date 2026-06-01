## ADDED Requirements

### Requirement: Canonical AI layout separates agents and skills
The system SHALL use `.ai/agents` and `.ai/skills` as the canonical active source layout for Mires runtime guidance.

#### Scenario: Maintainer locates public agents
- **WHEN** a maintainer needs to inspect public Mires agent entrypoints
- **THEN** each public agent entrypoint is available under `.ai/agents/<agent-name>/`
- **AND** the public agent directory contains an agent instruction document describing when and how to use that agent
- **AND** the public agent directory contains the runtime metadata needed to export that agent

#### Scenario: Maintainer locates skill packages
- **WHEN** a maintainer needs to inspect reusable skills, compatibility redirects, or detailed references
- **THEN** those assets are available under `.ai/skills/<skill-name>/`
- **AND** detailed reference material remains owned by the public agent or support skill documented for that material

### Requirement: AI agents follow the requested Mires hierarchy
The system SHALL create the requested hierarchical agent tree under `.ai/agents`.

#### Scenario: Top-level agents exist
- **WHEN** maintainers inspect `.ai/agents`
- **THEN** it contains `mires-planner`, `mires-explorer`, `mires-tester`, `mires-researcher`, `mires-backend`, and `mires-frontend`
- **AND** each top-level directory contains agent usage instructions

#### Scenario: Tester subagents exist
- **WHEN** maintainers inspect `.ai/agents/mires-tester`
- **THEN** it contains `mires-tester-agent-browser` and `mires-tester-portless`
- **AND** each tester subagent contains focused usage instructions for its verification mode

#### Scenario: Backend Python subagents exist
- **WHEN** maintainers inspect `.ai/agents/mires-backend/mires-python`
- **THEN** it contains `mires-python-sqlalchemy`, `mires-python-aws`, `mires-python-tdd`, `mires-python-patterns`, `mires-python-class-based`, `mires-python-function-based`, `mires-python-fastapi`, and `mires-python-django`
- **AND** each Python subagent contains focused usage instructions for its backend concern

#### Scenario: FastAPI subagents exist
- **WHEN** maintainers inspect `.ai/agents/mires-backend/mires-python/mires-python-fastapi`
- **THEN** it contains `mires-python-fastapi-sqlalchemy`, `mires-python-fastapi-postgres`, `mires-python-fastapi-tdd`, `mires-python-fastapi-celery`, and `mires-python-fastapi-celery-beat`
- **AND** each FastAPI subagent contains focused usage instructions for its FastAPI concern

#### Scenario: Django subagents exist
- **WHEN** maintainers inspect `.ai/agents/mires-backend/mires-python/mires-python-django`
- **THEN** it contains `mires-python-django-models`, `mires-python-django-serializer`, `mires-python-django-apis`, `mires-python-django-apps`, `mires-python-django-tests`, `mires-python-django-celery`, `mires-python-django-celery-beat`, `mires-python-django-patterns`, and `mires-python-django-tdd`
- **AND** each Django subagent contains focused usage instructions for its Django concern

#### Scenario: Frontend React subagents exist
- **WHEN** maintainers inspect `.ai/agents/mires-frontend/mires-react`
- **THEN** it contains `mires-react-query`, `mires-react-hook-form`, and `mires-zod`
- **AND** each React subagent contains focused usage instructions for its frontend concern

### Requirement: Agent instructions define usage and delegation
Each `.ai/agents` directory SHALL document when the agent is used, what inputs it needs, what outputs it produces, and which subagents or skills it may call.

#### Scenario: Planner documents agent usage
- **WHEN** maintainers open `.ai/agents/mires-planner`
- **THEN** the agent instructions explain how to choose and use the Mires agents in the hierarchy

#### Scenario: Explorer documents error discovery
- **WHEN** maintainers open `.ai/agents/mires-explorer`
- **THEN** the agent instructions explain how it calls relevant subagents to explore code and identify bugs, errors, and risks

#### Scenario: Tester documents exploration handoff
- **WHEN** maintainers open `.ai/agents/mires-tester`
- **THEN** the agent instructions explain how it validates working behavior
- **AND** the instructions require it to call or consult `mires-explorer` when checking for bugs or issues

#### Scenario: Researcher documents internet research
- **WHEN** maintainers open `.ai/agents/mires-researcher`
- **THEN** the agent instructions explain how to use MCPs or WebSearch for current internet research
- **AND** the instructions require implementation references or citations when internet research informs guidance

### Requirement: AI layout preserves Mires identifiers
The system SHALL preserve existing Mires agent and skill identifiers when moving assets into `.ai/agents` and `.ai/skills`.

#### Scenario: Public agent is moved
- **WHEN** a public agent is represented in `.ai/agents/<agent-name>/`
- **THEN** its Mires identifier remains unchanged
- **AND** any exported Codex skill keeps compatible front matter and invocation naming

#### Scenario: Compatibility skill is moved
- **WHEN** a compatibility redirect skill is represented in `.ai/skills/<skill-name>/`
- **THEN** its Mires identifier remains unchanged
- **AND** it continues to redirect to an owning public agent

### Requirement: Codex export mirrors canonical AI assets
The system SHALL provide a Codex-compatible `.codex/skills` export from the canonical `.ai` layout while Codex requires that runtime path.

#### Scenario: Codex runtime assets are prepared
- **WHEN** the repository prepares active Codex runtime assets
- **THEN** `.codex/skills` contains exported skill packages derived from `.ai/agents` and `.ai/skills`
- **AND** the exported packages preserve current Codex skill discovery behavior

#### Scenario: Compatibility export is verified
- **WHEN** maintainers run the documented verification command
- **THEN** the command validates that `.codex/skills` does not drift from the canonical `.ai` assets
- **AND** it reports missing, stale, or incorrectly exported agent and skill packages

### Requirement: Documentation uses canonical AI paths
The system SHALL document `.ai/agents` and `.ai/skills` as the canonical authoring paths for active Mires assets.

#### Scenario: Contributor reads repository guidance
- **WHEN** a contributor reads active repository guidance
- **THEN** the guidance explains that `.ai/agents` and `.ai/skills` are canonical
- **AND** it explains that `.codex/skills` is a compatibility export for Codex runtime consumption

#### Scenario: Documentation references moved paths
- **WHEN** active documentation links to agent, skill, reference, script, or docs paths
- **THEN** the referenced paths exist
- **AND** canonical source references use `.ai` paths unless describing the Codex compatibility export
