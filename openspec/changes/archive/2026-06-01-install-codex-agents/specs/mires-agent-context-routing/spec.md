## ADDED Requirements

### Requirement: Canonical agents can be installed into Codex runtime
The system SHALL allow canonical `.ai/agents` entries to be transformed into Codex-installed agent files without treating the installed files as canonical source assets.

#### Scenario: Codex installation derives runtime files
- **WHEN** maintainers install Mires agents for Codex
- **THEN** the installed Codex files are generated from `.ai/agents/<agent-name>/AGENT.md` and associated runtime metadata
- **AND** the canonical public agent source remains under `.ai/agents/<agent-name>/`
- **AND** the installed `$HOME/.codex/agents/` files are not required to be committed to the Mires repository

#### Scenario: Runtime routing source is inspected
- **WHEN** maintainers inspect active repository routing sources
- **THEN** `.ai/agents` remains the public agent-first authoring hierarchy
- **AND** Codex-installed files are treated as adapter output rather than a second maintained routing tree
