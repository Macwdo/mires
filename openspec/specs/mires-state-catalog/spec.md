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

### Requirement: Skills are aggregated by domain
The system SHALL expose one skill per domain and SHALL carry per-library or per-practice guidance as a topic inside the owning domain rather than as its own catalog entry.

#### Scenario: Guidance for a library is added
- **WHEN** a maintainer adds guidance for a library or practice that belongs to an existing domain
- **THEN** it is written as `skills/<domain>/references/<topic>/rules.md` with its focused documents beside it
- **AND** the domain's `SKILL.md` routes to that rule document
- **AND** no new entry is added to the `skills` section of `state.yml`

#### Scenario: A topic is not routed
- **WHEN** a topic directory under a skill's `references/` has no `rules.md`, or the skill's `SKILL.md` does not reference it
- **THEN** the test suite reports the unrouted topic and fails

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

### Requirement: One command installs every runtime
The system SHALL install the whole catalog into every supported runtime from a single command, without requiring a clone of the repository.

#### Scenario: A machine is provisioned from scratch
- **WHEN** a maintainer runs the published entry point with no arguments beyond `install`
- **THEN** the catalog is installed into Codex, Cursor, Claude Code, and OpenCode
- **AND** the catalog is read from the copy shipped inside the package when no `state.yml` is found in the working directory or its parents

#### Scenario: A runtime cannot express an asset kind
- **WHEN** a target has no runtime for an asset kind, such as hooks in Codex
- **THEN** that kind is skipped and the command reports which kinds were skipped for that target

#### Scenario: A runtime has no direct location for an asset kind
- **WHEN** a target supports an asset kind only through an indirection, as Cursor does for rules
- **THEN** the adapter uses that runtime's documented mechanism rather than writing to a path the runtime never reads

#### Scenario: A single runtime is targeted
- **WHEN** a maintainer passes `--target` with one runtime slug
- **THEN** only that runtime is written to
- **AND** an unknown slug fails with the list of supported targets

### Requirement: Installs are idempotent and remove what they no longer own
The system SHALL record what each install wrote and SHALL remove exactly that on the next install, without disturbing configuration the user owns.

#### Scenario: The same install runs twice
- **WHEN** an install runs a second time with no catalog change
- **THEN** the resulting files are byte-for-byte identical to the first run

#### Scenario: An entry is dropped from the catalog or the profile
- **WHEN** an install runs after an entry is removed from `state.yml` or from the selected profile
- **THEN** the files and configuration keys that entry owned are removed from the runtime

#### Scenario: A runtime file also holds the user's own configuration
- **WHEN** an install writes to a shared file such as `CLAUDE.md`, `mcp.json`, `hooks.json`, or `config.toml`
- **THEN** only the Mires block or the Mires keys are replaced
- **AND** servers, hooks, and prose the user owns are preserved

### Requirement: Hooks are declared in a runtime-neutral vocabulary
The system SHALL accept hooks bound only to canonical Mires events and SHALL translate them into each runtime's own event names.

#### Scenario: A hook binds to an unknown event
- **WHEN** a `hooks.json` binds an event outside the canonical vocabulary
- **THEN** validation reports the unknown event and lists the known ones

#### Scenario: A hook is installed into a runtime with different event names
- **WHEN** a canonical event is installed into a runtime that names it differently
- **THEN** it is written using that runtime's event name and matcher
- **AND** the command it runs points at the copy installed under the runtime home, not at the repository

### Requirement: Validation precedes any runtime write
The system SHALL validate the catalog before checking or installing a runtime target.

#### Scenario: The catalog is broken at install time
- **WHEN** a maintainer installs while `state.yml` disagrees with the files on disk
- **THEN** the command reports the catalog errors and exits without writing runtime output

#### Scenario: A supported target is installed
- **WHEN** the catalog is valid and the target is `codex` or `opencode`
- **THEN** generated output is written only under the target's home directory
- **AND** the generated output contains no reference to the repository's `subagents/` source tree
