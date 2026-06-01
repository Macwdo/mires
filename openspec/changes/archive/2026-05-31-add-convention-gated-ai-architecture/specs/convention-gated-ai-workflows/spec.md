## ADDED Requirements

### Requirement: Backend work requires convention discovery
The system SHALL require project-conventions discovery before backend implementation work that touches configuration, database access, dependency injection, services, repositories, error handling, testing, app startup, Celery, Django, FastAPI, or generic Python backend modules.

#### Scenario: Backend implementation starts with repository inspection
- **WHEN** an agent is asked to implement backend code
- **THEN** the agent produces a convention report with evidence from repository files before editing code

#### Scenario: Unclear conventions are reported
- **WHEN** repository inspection does not reveal a clear convention for an affected backend concern
- **THEN** the agent reports the uncertainty instead of silently inventing a new architecture

### Requirement: Convention report covers backend drift risks
The system SHALL define the minimum convention report fields needed to prevent backend implementation drift.

#### Scenario: Convention report includes required backend fields
- **WHEN** the project-conventions workflow runs
- **THEN** it records the discovered configuration pattern, database/session pattern, dependency-injection style, service or repository boundaries, error-handling style, testing style, naming style, and module organization

#### Scenario: Convention report cites evidence
- **WHEN** a convention is recorded
- **THEN** the report includes the repository files or configuration sources that support that conclusion

### Requirement: Existing project conventions override generic guidance
The system SHALL make current repository conventions higher priority than generic Mires examples, external best practices, and source-repo examples embedded in skills.

#### Scenario: Existing configuration pattern is reused
- **WHEN** a project already uses Pydantic Settings, Dynaconf, Django settings, environment-only configuration, or another established settings pattern
- **THEN** the agent extends that pattern instead of introducing a competing configuration abstraction

#### Scenario: Existing database abstraction is reused
- **WHEN** a project already has a database engine, session factory, request dependency, Django initialization, or migration pattern
- **THEN** the agent reuses that pattern instead of creating duplicate database or session abstractions

#### Scenario: Generic examples conflict with current repository evidence
- **WHEN** a loaded skill example conflicts with conventions found in the target repository
- **THEN** the agent follows the target repository convention and treats the example as non-authoritative

### Requirement: Python settings changes use a dedicated settings skill
The system SHALL provide Python settings guidance that prevents accidental introduction of incompatible configuration patterns.

#### Scenario: Dataclass settings are rejected when stronger settings pattern exists
- **WHEN** a Python project already uses Pydantic Settings, Dynaconf, Django settings, or another established settings system
- **THEN** the agent does not introduce dataclass-based application settings

#### Scenario: New settings fields are added to existing settings surface
- **WHEN** a backend change requires new configuration values
- **THEN** the agent adds them to the existing settings module, class, or framework settings surface used by the repository

### Requirement: Backend orchestration sequences implementation safely
The system SHALL provide a backend orchestrator workflow that sequences convention discovery, skill selection, implementation, validation, and review.

#### Scenario: Orchestrator selects skills after discovery
- **WHEN** backend implementation requires Mires skills
- **THEN** the backend orchestrator selects only relevant skills after reading the convention report

#### Scenario: Orchestrator validates before final response
- **WHEN** backend implementation changes are complete
- **THEN** the backend orchestrator runs or reports the focused validation appropriate for the touched files

### Requirement: Backend review blocks convention drift
The system SHALL provide a backend review gate that checks implementation against the convention report and relevant Mires skills.

#### Scenario: Review flags new unapproved abstractions
- **WHEN** a change introduces a new configuration, database, session, dependency-injection, service, repository, or testing abstraction without evidence that no existing convention applies
- **THEN** the backend reviewer reports the change as convention drift

#### Scenario: Review checks tests and validation
- **WHEN** backend behavior changes
- **THEN** the backend reviewer checks whether tests or focused validation match the repository's existing testing style

### Requirement: Guidance remains adaptable across agent runtimes
The system SHALL keep the new convention-gated workflow content portable while using Codex-compatible adapters for the first implementation.

#### Scenario: Codex remains first active adapter
- **WHEN** the first implementation is applied
- **THEN** the new workflows are available through Mires Codex skills and optional Codex agent metadata

#### Scenario: Runtime-specific metadata does not own the behavior
- **WHEN** a workflow has runtime-specific adapter metadata
- **THEN** the normative behavior remains in Markdown guidance that can be adapted to another agent runtime later
