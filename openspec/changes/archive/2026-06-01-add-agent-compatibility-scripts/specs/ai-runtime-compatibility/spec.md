## ADDED Requirements

### Requirement: Canonical AI assets are parsed into runtime-neutral models
The system SHALL provide a Python compatibility layer that reads canonical `.ai/agents` and `.ai/skills` assets into runtime-neutral models before applying runtime-specific behavior.

#### Scenario: Agent assets are parsed
- **WHEN** the compatibility workflow reads `.ai/agents/<agent-name>/AGENT.md`
- **THEN** it captures the agent name, description, parent, children, source path, and associated runtime metadata path when present
- **AND** it does not require runtime-specific authoring fields in the canonical `AGENT.md`

#### Scenario: Skill assets are parsed
- **WHEN** the compatibility workflow reads `.ai/skills/<skill-name>/SKILL.md`
- **THEN** it captures the skill name, description, source path, and reference paths declared by the owner skill
- **AND** it treats the skill package as canonical runtime-agnostic source material

### Requirement: Compatibility workflow has a Python entrypoint
The system SHALL expose compatibility operations through `src/main.py`.

#### Scenario: Maintainer runs the entrypoint
- **WHEN** a maintainer runs the documented Python entrypoint from the repository root
- **THEN** the entrypoint loads canonical `.ai` assets through `src/compatibility`
- **AND** it reports compatibility results without requiring network access

#### Scenario: Invalid assets are discovered
- **WHEN** the entrypoint encounters missing required front matter, broken reference paths, or invalid runtime metadata for a requested target
- **THEN** it exits unsuccessfully
- **AND** it reports the affected path and validation reason

### Requirement: Codex is the first supported runtime adapter
The system SHALL implement Codex compatibility as the first concrete runtime adapter.

#### Scenario: Codex compatibility runs
- **WHEN** the compatibility workflow is invoked for the Codex target
- **THEN** it applies Codex-specific checks or transformations from the normalized `.ai` models
- **AND** shared parsing remains independent of Codex-specific modules

#### Scenario: Unsupported runtime is requested
- **WHEN** a maintainer requests a runtime target other than Codex before that adapter exists
- **THEN** the compatibility workflow fails with a clear unsupported-target message
- **AND** it does not create partial runtime-specific outputs

### Requirement: Runtime adapters do not create a second authoring tree
The system SHALL keep `.ai/agents` and `.ai/skills` as the only active authoring source for agent and skill assets.

#### Scenario: Runtime-specific output is needed
- **WHEN** an adapter needs runtime-specific output
- **THEN** the output is derived from canonical `.ai` assets
- **AND** maintainers are not required to edit a second committed runtime asset tree

#### Scenario: Future runtimes are added
- **WHEN** a future runtime such as OpenCode is supported
- **THEN** it is added as a new adapter under `src/compatibility`
- **AND** shared parsing and normalized models remain reusable across runtime targets
