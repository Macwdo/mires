# mires-state-catalog Specification

## Purpose
Define how Mires declares its catalog of skills, subagents, rules, MCP servers, and hooks in `state.yml`, how profiles select from that catalog, and how the declaration is validated against the files on disk.

This capability supersedes `mires-agent-context-routing` and `mires-namespace-distribution`, which described the earlier `.ai/` runtime tree and a granular agent hierarchy.

## Requirements

### Requirement: state.yml is the single catalog definition
The system SHALL declare every catalog entry in `state.yml` and SHALL NOT hardcode catalog membership anywhere else.

#### Scenario: A catalog entry is added
- **WHEN** a maintainer adds files for a skill, subagent, rule, MCP server, or hook
- **THEN** validation fails until the entry is declared in `state.yml`
- **AND** the entry resolves to `<section>/<slug>` unless an explicit `path` overrides it

#### Scenario: A declaration has no files
- **WHEN** `state.yml` declares an entry whose directory or required artifact is missing
- **THEN** validation reports the missing path and fails

#### Scenario: A verification tool needs the catalog
- **WHEN** a script or test needs to know which entries exist
- **THEN** it reads `state.yml` rather than maintaining its own list

### Requirement: Entries carry a consistent identity
The system SHALL require each entry to declare a kebab-case `slug`, a `name`, and a `description`, unique within its section.

#### Scenario: An invalid or duplicated slug is declared
- **WHEN** a slug is not kebab-case, exceeds 64 characters, or repeats within a section
- **THEN** loading `state.yml` fails with the offending field and slug

#### Scenario: Front matter disagrees with the declaration
- **WHEN** a `SKILL.md` or `AGENT.md` front matter `name` differs from the declared slug
- **THEN** validation reports the mismatch and fails

### Requirement: Skill visibility selects the validation contract
The system SHALL validate a skill according to its declared `visibility`.

#### Scenario: A private skill is validated
- **WHEN** a skill declares `visibility: private`
- **THEN** its `SKILL.md` must contain the sections `## When To Use`, `## Core Rules`, `## Preferred Patterns`, `## Anti-Patterns`, `## Checklist`, and `## References Index`

#### Scenario: A public skill is validated
- **WHEN** a skill declares `visibility: public`
- **THEN** it must ship `agents/openai.yaml` invoking `$<slug>`

### Requirement: Profiles select a subset of the catalog
The system SHALL allow profiles to name the entries they use, and SHALL install only that subset when a profile is selected.

#### Scenario: A profile references an unknown entry
- **WHEN** a profile names a slug absent from the matching catalog section
- **THEN** validation reports the profile, the section, and the unknown slug

#### Scenario: An install selects a profile
- **WHEN** a maintainer runs an install with `--profile <slug>`
- **THEN** only the subagents and skills that profile selects are installed
- **AND** an unknown profile slug fails with the list of known profiles

#### Scenario: An install omits a profile
- **WHEN** no profile is given
- **THEN** the whole declared catalog is installed

### Requirement: Validation precedes any runtime write
The system SHALL validate the catalog before checking or installing a runtime target.

#### Scenario: The catalog is broken at install time
- **WHEN** a maintainer installs while `state.yml` disagrees with the files on disk
- **THEN** the command reports the catalog errors and exits without writing runtime output

#### Scenario: A supported target is installed
- **WHEN** the catalog is valid and the target is `codex` or `opencode`
- **THEN** generated output is written only under the target's home directory
- **AND** the generated output contains no reference to the repository's `subagents/` source tree
