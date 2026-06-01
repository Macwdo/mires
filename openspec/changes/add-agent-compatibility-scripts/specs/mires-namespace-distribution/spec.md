## ADDED Requirements

### Requirement: Distribution may include Python compatibility tooling
The system SHALL allow active distribution to include Python compatibility scripts that derive runtime support from canonical `.ai` assets.

#### Scenario: Active repository is inspected
- **WHEN** active repository files are inspected outside archived OpenSpec history
- **THEN** `src/main.py` and `src/compatibility/**` may exist as compatibility tooling
- **AND** their behavior derives from canonical `.ai/agents` and `.ai/skills` assets

#### Scenario: Verification runs with compatibility tooling present
- **WHEN** maintainers run the documented verification command
- **THEN** it accepts Python compatibility tooling as active product source
- **AND** it still fails on duplicate runtime authoring trees

### Requirement: Documentation distinguishes source assets from compatibility adapters
The system SHALL document that `.ai` assets are canonical source assets and Python compatibility modules are runtime adapters.

#### Scenario: Maintainer reads compatibility documentation
- **WHEN** a maintainer reads active documentation for runtime support
- **THEN** it identifies `.ai/agents` and `.ai/skills` as runtime-agnostic source paths
- **AND** it identifies Codex support as an adapter-managed compatibility target
- **AND** it does not instruct maintainers to edit runtime-specific duplicate assets
