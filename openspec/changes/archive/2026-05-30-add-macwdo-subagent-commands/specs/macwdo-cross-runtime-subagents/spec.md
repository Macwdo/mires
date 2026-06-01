## ADDED Requirements

### Requirement: Package SHALL include OpenCode tester and reviewer assets
The Macwdo distribution SHALL package OpenCode skill assets for `macwdo-tester` and `macwdo-reviewer` plus matching OpenCode slash command files.

#### Scenario: Bundled assets include both OpenCode entrypoints
- **WHEN** maintainers inspect the packaged asset set or run package verification
- **THEN** the package MUST include `.opencode/skills/macwdo-tester/SKILL.md` and `.opencode/skills/macwdo-reviewer/SKILL.md`
- **AND** it MUST include `.opencode/commands/macwdo-tester.md` and `.opencode/commands/macwdo-reviewer.md`

### Requirement: OpenCode commands SHALL route to the matching Macwdo skills
Each OpenCode slash command for these entrypoints SHALL direct the runtime to use the corresponding Macwdo skill as the source of workflow guidance.

#### Scenario: Tester command routes to tester skill
- **WHEN** a user invokes the `macwdo-tester` OpenCode command
- **THEN** the command MUST instruct OpenCode to use the `macwdo-tester` skill
- **AND** the detailed testing workflow MUST live in the skill file instead of being duplicated in the command

#### Scenario: Reviewer command routes to reviewer skill
- **WHEN** a user invokes the `macwdo-reviewer` OpenCode command
- **THEN** the command MUST instruct OpenCode to use the `macwdo-reviewer` skill
- **AND** the detailed review workflow MUST live in the skill file instead of being duplicated in the command

### Requirement: Cross-runtime install SHALL expose the same named entrypoints
The existing installer targets for `codex`, `opencode`, and `both` SHALL expose `macwdo-tester` and `macwdo-reviewer` in the selected runtime without requiring manual asset copying.

#### Scenario: OpenCode install exposes tester and reviewer entrypoints
- **WHEN** a user installs the package with `--target opencode` or `--target both`
- **THEN** the installed OpenCode `skills/` directory MUST contain `macwdo-tester` and `macwdo-reviewer`
- **AND** the installed OpenCode `commands/` directory MUST contain `macwdo-tester.md` and `macwdo-reviewer.md`

#### Scenario: Codex install keeps existing named entrypoints
- **WHEN** a user installs the package with `--target codex` or `--target both`
- **THEN** the installed Codex `skills/` directory MUST continue to contain `macwdo-tester` and `macwdo-reviewer`
- **AND** their bundled `agents/openai.yaml` files MUST remain intact
