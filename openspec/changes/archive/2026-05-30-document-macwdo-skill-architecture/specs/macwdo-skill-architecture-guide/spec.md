## ADDED Requirements

### Requirement: Repository skill architecture is documented
The project SHALL provide documentation that explains how Macwdo skills, OpenCode assets, agent configs, and OpenSpec changes are organized in this repository.

#### Scenario: Reader needs repository orientation
- **WHEN** a reader opens the architecture guide
- **THEN** the guide describes the purpose of `.codex/skills/`, `.opencode/skills/`, `.opencode/commands/`, `openspec/changes/`, and agent configuration files

### Requirement: Macwdo skill hierarchy roles are explained
The project SHALL document the intended roles of namespace skills, explorer/router skills, leaf implementation skills, workflow skills, and agent-backed skills.

#### Scenario: Reader evaluates a skill file
- **WHEN** a reader compares a skill against the architecture guide
- **THEN** the reader can classify it as a namespace, router, leaf, workflow, or agent-backed skill based on documented criteria

### Requirement: Skill structure evaluation guidance is included
The project SHALL include guidance for deciding whether the current structure is appropriate and how future implementation preferences should be added.

#### Scenario: Reader wants to add new guidance
- **WHEN** a reader wants to add a new Macwdo implementation preference
- **THEN** the guide explains whether it belongs in an existing leaf, a new leaf, a router map, an OpenCode command, or an agent-backed workflow

### Requirement: Current structure is assessed with recommendations
The project SHALL include a practical assessment of the current Macwdo skill structure, including strengths, risks, and recommended maintenance practices.

#### Scenario: Reader asks if the current approach is good
- **WHEN** a reader wants to know whether the Markdown skill structure is a good way to encode implementation preferences
- **THEN** the guide gives a direct assessment with concrete reasons and follow-up recommendations
