## ADDED Requirements

### Requirement: Planner selects and loads relevant Macwdo skills
The system SHALL provide a `macwdo-planner` skill that inspects the user's request and repository context, selects relevant Macwdo skills through the namespace or explorer map, and loads the selected skill guidance before producing an implementation plan.

#### Scenario: Planning a FastAPI endpoint
- **WHEN** the user asks for a plan to add a FastAPI endpoint
- **THEN** the planner identifies FastAPI-related Macwdo skills such as `macwdo-python-fastapi-patterns` and includes their guidance in the planning context

### Requirement: Planner produces a decision-complete implementation plan
The `macwdo-planner` skill SHALL produce a plan that identifies selected skills, intended implementation approach, likely files or modules to touch, edge cases, and validation steps.

#### Scenario: Planning output is actionable
- **WHEN** the planner finishes analyzing a request
- **THEN** the output contains enough implementation detail for another engineer or agent to execute without choosing additional architecture or skill-routing decisions

### Requirement: Planner does not mutate code during planning
The `macwdo-planner` skill SHALL treat planning as non-mutating work and avoid editing files or applying code changes while preparing a plan.

#### Scenario: Planning-only request
- **WHEN** the user asks the planner to plan an implementation
- **THEN** the planner inspects files and skills but does not modify repository files as part of planning

### Requirement: Reviewer inspects current code and git diff before findings
The `macwdo-reviewer` agent prompt SHALL direct the reviewer to inspect current code, git state, changed files, and relevant Macwdo skills before presenting findings.

#### Scenario: Reviewing local changes
- **WHEN** the user asks the reviewer to review the current change
- **THEN** the reviewer uses repository context such as `git status`, `git diff`, and targeted file reads before producing a findings-first review

### Requirement: Planner is discoverable through Macwdo routers
The system SHALL list `macwdo-planner` in both the `macwdo` namespace skill and the `macwdo-explorer` skill map.

#### Scenario: Discovering planning support
- **WHEN** an agent loads the Macwdo namespace or explorer skill to find planning guidance
- **THEN** the skill map includes `macwdo-planner` with its path
