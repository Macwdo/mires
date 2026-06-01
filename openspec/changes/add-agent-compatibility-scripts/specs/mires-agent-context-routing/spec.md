## ADDED Requirements

### Requirement: Agent routing assets are runtime-agnostic compatibility inputs
The system SHALL treat canonical `.ai/agents` and `.ai/skills` routing assets as runtime-agnostic inputs for compatibility tooling.

#### Scenario: Compatibility tooling reads agent routing
- **WHEN** Python compatibility tooling inspects Mires routing behavior
- **THEN** it reads the canonical `.ai/agents` hierarchy and `.ai/skills` owner packages
- **AND** it does not require agents or skills to include Codex-only authoring content

#### Scenario: Runtime-specific behavior is needed
- **WHEN** Codex-specific behavior is required for Mires agents or skills
- **THEN** the behavior is handled by the Codex compatibility adapter
- **AND** the public routing contract remains defined by canonical `.ai` assets

### Requirement: Orchestrator-first behavior remains canonical
The system SHALL preserve orchestrator-first routing as the canonical behavior while compatibility scripts are added.

#### Scenario: Non-trivial engineering work is requested
- **WHEN** a user requests medium or complex engineering work
- **THEN** the canonical routing path still starts from `.ai/agents/orchestrator/AGENT.md`
- **AND** compatibility tooling does not bypass or replace the orchestrator-first contract
