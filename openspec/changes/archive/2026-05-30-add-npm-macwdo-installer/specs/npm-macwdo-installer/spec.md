## ADDED Requirements

### Requirement: npm package exposes Macwdo CLI
The system SHALL provide a publishable npm package named `@macwdo/macwdo` that exposes a `macwdo` executable command.

#### Scenario: Global npm install links command
- **WHEN** a user installs the package with `npm install -g @macwdo/macwdo`
- **THEN** npm links the package executable as `macwdo`

#### Scenario: CLI reports version
- **WHEN** a user runs `macwdo --version`
- **THEN** the CLI prints the package version from the installed package metadata

#### Scenario: CLI reports help
- **WHEN** a user runs `macwdo --help`
- **THEN** the CLI prints available commands and install scope options

### Requirement: CLI supports local package usage
The system SHALL support running the `macwdo` CLI from a project-local npm installation.

#### Scenario: Local install exposes executable to npm scripts
- **WHEN** a project installs `@macwdo/macwdo` as a local dependency
- **THEN** the `macwdo` executable is available to npm scripts for that project

#### Scenario: npm exec can run local CLI
- **WHEN** a user runs the package through `npm exec` or `npx`
- **THEN** the same `macwdo` CLI commands are available without requiring a global package install

### Requirement: Installer copies bundled skills and subagents
The system SHALL install every bundled skill package from `.codex/skills/` and preserve each skill package's relative file structure.

#### Scenario: Install all skills by default
- **WHEN** a user runs `macwdo install`
- **THEN** every bundled directory under `.codex/skills/` is selected for installation

#### Scenario: Preserve subagent configs
- **WHEN** a bundled skill contains files under `agents/`
- **THEN** the installer copies those files to the matching installed skill directory

#### Scenario: Preserve supporting skill files
- **WHEN** a bundled skill contains `references`, `scripts`, `assets`, or other package-local files
- **THEN** the installer copies those files with relative paths preserved

### Requirement: Installer supports user and project scopes
The system SHALL let the user choose whether skills are installed into the user-level Codex skills directory or a project-local Codex skills directory.

#### Scenario: User scope targets Codex home
- **WHEN** a user runs `macwdo install --scope user`
- **THEN** the installer targets `$CODEX_HOME/skills` when `CODEX_HOME` is set and otherwise targets `~/.codex/skills`

#### Scenario: Project scope targets selected project
- **WHEN** a user runs `macwdo install --scope project --project-root <path>`
- **THEN** the installer targets `<path>/.codex/skills`

#### Scenario: Project scope defaults to current directory
- **WHEN** a user runs `macwdo install --scope project` without `--project-root`
- **THEN** the installer targets `.codex/skills` under the current working directory

#### Scenario: Interactive scope prompt
- **WHEN** a user runs `macwdo install` in an interactive terminal without a scope option
- **THEN** the CLI prompts the user to choose user-level or project-level installation before writing files

### Requirement: Installer prevents accidental overwrites
The system SHALL detect existing destination skill directories and avoid replacing them unless the user explicitly confirms replacement.

#### Scenario: Existing skill prompts before overwrite
- **WHEN** the destination already contains a skill directory with the same name as a bundled skill
- **THEN** the installer prompts the user to overwrite or skip that skill

#### Scenario: Declined overwrite preserves destination
- **WHEN** the user declines overwrite for an existing skill directory
- **THEN** the installer leaves the existing destination skill directory unchanged

#### Scenario: Force overwrites conflicts
- **WHEN** the user runs `macwdo install --force`
- **THEN** the installer replaces conflicting destination skill directories without per-skill prompts

#### Scenario: Non-interactive install avoids implicit destructive writes
- **WHEN** the installer is run without an interactive terminal and without `--force`
- **THEN** conflicting destination skill directories are not overwritten automatically

### Requirement: Installer supports dry-run reporting
The system SHALL provide a dry-run mode that reports planned installation actions without writing files.

#### Scenario: Dry-run lists destination and counts
- **WHEN** a user runs `macwdo install --dry-run`
- **THEN** the CLI prints the resolved destination, selected skill count, conflicts, and planned copy actions

#### Scenario: Dry-run does not change filesystem
- **WHEN** dry-run mode is enabled
- **THEN** the installer creates no directories, copies no files, and removes no existing files

### Requirement: Package contents are validated before publish
The system SHALL provide verification commands that prove the npm package includes the CLI and all bundled skill assets before publication.

#### Scenario: Pack dry-run includes required assets
- **WHEN** maintainers run the package dry-run validation
- **THEN** the reported package contents include the CLI entry point, package metadata, documentation, every `SKILL.md`, and every bundled `agents/openai.yaml`

#### Scenario: Packed tarball installs skills
- **WHEN** maintainers install from a locally generated npm tarball in a temporary directory
- **THEN** the `macwdo install` command copies all bundled skills and subagent files to the requested destination

### Requirement: Documentation covers npm installation workflows
The system SHALL document global npm installation, local npm usage, skill install scopes, overwrite behavior, and validation commands.

#### Scenario: User follows global install docs
- **WHEN** a user reads the documentation for global npm installation
- **THEN** they can identify how to install `@macwdo/macwdo` globally and run `macwdo install --scope user`

#### Scenario: User follows project install docs
- **WHEN** a user reads the documentation for project-local skill installation
- **THEN** they can identify how to install or run the npm package locally and copy skills into a chosen project's `.codex/skills` directory

#### Scenario: Maintainer follows publish validation docs
- **WHEN** a maintainer reads the release documentation
- **THEN** they can identify the commands required to verify package contents before publishing
