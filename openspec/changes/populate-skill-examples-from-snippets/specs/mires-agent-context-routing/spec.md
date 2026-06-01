## MODIFIED Requirements

### Requirement: Granular implementation guidance is not default public context
The system SHALL keep granular implementation guidance outside the default public routing surface and store it as agent-owned or workflow-owned references, including concrete examples when they are needed to make the selected guidance actionable.

#### Scenario: Granular guidance is retained
- **WHEN** detailed Python, Django, FastAPI, LangGraph, React, Next.js, testing, or DevEx guidance remains useful
- **THEN** it is stored as agent-owned reference material or private support guidance loaded only by the owning agent
- **AND** its canonical source path is under `.ai/skills`

#### Scenario: Concrete examples are added to retained guidance
- **WHEN** local snippet material demonstrates a pattern owned by a specialized Mires agent or skill reference
- **THEN** the adapted example is stored under the owning `.ai/skills/**/references` path
- **AND** the example does not create a new public routing entry, standalone granular skill, or duplicate runtime asset tree
