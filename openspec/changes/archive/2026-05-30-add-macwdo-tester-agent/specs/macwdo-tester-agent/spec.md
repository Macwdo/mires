## ADDED Requirements

### Requirement: Tester provides a unified Macwdo testing entrypoint
The system SHALL provide a `macwdo-tester` skill and agent configuration as the canonical entrypoint for Macwdo local app verification.

#### Scenario: User requests Macwdo testing
- **WHEN** a user asks to test or verify a local app flow with Macwdo conventions
- **THEN** the available Macwdo testing entrypoint is `macwdo-tester`

### Requirement: Tester composes portless and agent-browser guidance
The tester SHALL use the `portless` skill for routed local dev server URLs and the `agent-browser` skill for browser automation command details.

#### Scenario: Tester prepares a browser verification run
- **WHEN** a local browser verification requires a dev server and browser automation
- **THEN** the tester loads or follows `portless` and `agent-browser` guidance instead of duplicating their full CLI references

### Requirement: Tester validates local routing before browser actions
The tester SHALL inspect the repository and runtime context before opening a browser, including linked-worktree status when applicable, startup command, URL-sensitive environment settings, and routed portless URL.

#### Scenario: Routed URL is not established
- **WHEN** the tester cannot establish a valid portless routed URL
- **THEN** the tester stops before browser interaction and reports the concrete blocker

### Requirement: Tester verifies through snapshot-driven browser workflow
The tester SHALL use a browser verification loop that opens the routed URL, captures a baseline snapshot, interacts through current element references, waits for state changes, and verifies expected outcomes.

#### Scenario: Browser flow changes page state
- **WHEN** the tester performs an interaction that changes the page, URL, network state, or DOM
- **THEN** the tester refreshes browser context with a wait and snapshot before continuing

### Requirement: Tester stops at the first real blocker
The tester SHALL stop testing when it encounters a concrete blocker that invalidates the scenario and SHALL NOT continue clicking blindly after failure.

#### Scenario: Expected control is missing
- **WHEN** an expected control, route, text, or successful state is absent after appropriate waiting
- **THEN** the tester reports the missing expectation as the first blocker and stops the scenario

### Requirement: Tester reports concise verification results
The tester SHALL finish each verification run with a concise pass/fail report that includes branch or worktree context, routed URL, tested scenario, first blocker when failing, and dev-server shutdown status.

#### Scenario: Verification completes
- **WHEN** a tester run passes, fails, or is blocked
- **THEN** the final response includes the tested scenario, result, URL used, and cleanup status

### Requirement: Macwdo routers discover tester first
Macwdo router skills SHALL direct agent-testing requests to `macwdo-tester` instead of the old split `macwdo-agent-testing-*` workflow.

#### Scenario: Router receives an agent testing request
- **WHEN** `macwdo` or `macwdo-explorer` is used to select a testing skill
- **THEN** it selects `macwdo-tester` as the primary testing skill

### Requirement: Legacy agent-testing skills do not compete with tester
The old `macwdo-agent-testing-*` skills SHALL be removed or converted into compatibility redirects so they do not compete with `macwdo-tester` during skill discovery.

#### Scenario: Legacy testing skill is invoked
- **WHEN** a user or prompt still names a legacy `macwdo-agent-testing-*` skill
- **THEN** the guidance redirects to `macwdo-tester` or the legacy skill is absent from the active router map
