## MODIFIED Requirements

### Requirement: Distribution keeps granular guidance behind owner packages
The system SHALL keep useful granular implementation guidance inside canonical `.ai/skills` reference files owned by the relevant public agent or workflow package, including locally authored example material when it clarifies existing guidance.

#### Scenario: Existing prompt needs focused implementation detail
- **WHEN** a prompt needs narrow implementation guidance that was formerly surfaced as a standalone granular skill
- **THEN** the guidance is loaded from the owning agent or workflow package references under `.ai/skills`
- **AND** the public routing surface remains agent-first

#### Scenario: Granular skill is removed from the package
- **WHEN** maintainers decide a granular skill ID does not need compatibility preservation
- **THEN** active Mires documentation identifies the owning specialized agent or workflow package that now owns the reference material

#### Scenario: Local snippets inform owner references
- **WHEN** local `.snippets` files provide implementation examples for an existing owner reference
- **THEN** those examples may be adapted into the canonical `.ai/skills` reference material
- **AND** `.snippets` remains temporary source material rather than an installed runtime, package, or discovery surface
- **AND** the temporary `.snippets` source tree is removed after useful examples are migrated
