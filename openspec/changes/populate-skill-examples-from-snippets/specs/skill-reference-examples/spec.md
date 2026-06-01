## ADDED Requirements

### Requirement: Skill references include concrete examples
The system SHALL allow canonical `.ai/skills` reference files to include concrete implementation examples when those examples clarify existing agent-owned guidance.

#### Scenario: Reference guidance matches snippet source material
- **WHEN** a `.snippets/python` file demonstrates a pattern already covered by an `.ai/skills` reference
- **THEN** the relevant reference may include an adapted example for that pattern
- **AND** the example remains in the owning `.ai/skills/**/references` package

#### Scenario: Example belongs to a skill owner
- **WHEN** an example covers FastAPI, Celery, backend service boundaries, database lifecycle, Docker Compose, or Python tooling
- **THEN** the example is added to the matching existing owner reference
- **AND** the top-level `SKILL.md` remains a concise routing and reference index

### Requirement: Snippet-derived examples remain reusable
The system SHALL adapt snippet-derived examples so they are useful as guidance outside the source snippet project.

#### Scenario: Snippet contains project-specific imports
- **WHEN** a snippet uses project-specific modules, settings names, service names, or vendor dependencies
- **THEN** the reference either generalizes those names or labels the assumptions needed to reuse the example
- **AND** it does not present source-specific imports as universal requirements

#### Scenario: Snippet uses infrastructure-specific services
- **WHEN** a snippet demonstrates local infrastructure such as MinIO, LocalStack, SQS, S3, Postgres, or Redis
- **THEN** the reference explains the boundary or configuration pattern being demonstrated
- **AND** it avoids requiring that exact infrastructure for unrelated repositories

### Requirement: Example enrichment is validated
The system SHALL provide validation that enriched skill references remain reachable from the canonical `.ai` surface.

#### Scenario: Agent-first verification runs
- **WHEN** maintainers run `python3 scripts/verify_agent_first_surface.py`
- **THEN** the verifier passes with the enriched reference files present
- **AND** it does not require `.snippets` to become a runtime-discovered skill or agent surface

#### Scenario: Reference paths are inspected
- **WHEN** enriched references add or update relative links to `references/`, `agents/`, `scripts/`, or `assets/`
- **THEN** those paths exist in the repository
- **AND** documentation-only edits do not introduce broken owner-reference paths

### Requirement: Temporary snippet source is removed after migration
The system SHALL remove the temporary `.snippets` source tree after useful examples are migrated into canonical `.ai/skills` references.

#### Scenario: Snippet examples have been migrated
- **WHEN** useful `.snippets/python` examples have been adapted into the matching owner references
- **THEN** the implementation removes the `.snippets` tree from the active repository
- **AND** the canonical examples remain available under `.ai/skills/**/references`

#### Scenario: Repository is checked after migration
- **WHEN** maintainers inspect active repository files after the change is implemented
- **THEN** `.snippets` is not present as a long-lived parallel example library
- **AND** no public agent, skill, or package discovery behavior depends on `.snippets`
