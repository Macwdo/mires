## ADDED Requirements

### Requirement: Installer is a shell script
The system SHALL provide a shell script that can be run from the repository or a downloaded copy to install bundled Codex skills.

#### Scenario: Script runs from the repository
- **WHEN** a user executes the installer script from a cloned repository
- **THEN** the script starts an interactive installation flow

#### Scenario: Script runs from a downloaded copy
- **WHEN** a user executes the installer script from a downloaded source tree
- **THEN** the script uses the local `.codex/skills` content as the install source

### Requirement: Installer copies bundled skills
The system SHALL install Codex skills from the repository's bundled `.codex/skills` directory into the resolved destination directory.

#### Scenario: Install all bundled skills by default
- **WHEN** a user runs the installer without selecting a subset of skills
- **THEN** every bundled skill directory is copied to the destination skills directory

#### Scenario: Preserve skill package structure
- **WHEN** a bundled skill is installed
- **THEN** its `SKILL.md` and related `references`, `agents`, `scripts`, or `assets` files are copied with their relative paths preserved

### Requirement: Installer supports user and project scopes
The system SHALL support user-level and project-level installation scopes through interactive prompts.

#### Scenario: User scope resolves Codex home
- **WHEN** a user chooses user scope during the install prompt
- **THEN** the installer targets `$CODEX_HOME/skills` when `CODEX_HOME` is set and otherwise targets `~/.codex/skills`

#### Scenario: Project scope resolves project directory
- **WHEN** a user chooses project scope during the install prompt
- **THEN** the installer targets `.codex/skills` under the chosen project root

#### Scenario: Explicit destination overrides scope destination
#### Scenario: User confirms a custom install path
- **WHEN** a user provides a custom install path during the prompt flow
- **THEN** the installer writes to that destination instead of the default path for the selected scope

### Requirement: Installer prevents accidental destructive writes
The system SHALL ask before overwriting existing skill directories and leave them unchanged when the user declines.

#### Scenario: Existing skill blocks default install
- **WHEN** the destination already contains a skill directory with the same name
- **THEN** the installer prompts the user to choose whether to overwrite or skip it

#### Scenario: Overwrite replaces existing skill
- **WHEN** the user confirms overwrite for a conflicting skill
- **THEN** the installer replaces the destination skill directory with the bundled version

#### Scenario: Declined overwrite preserves the existing skill
- **WHEN** the user declines overwrite for a conflicting skill
- **THEN** the installer leaves the existing directory unchanged

### Requirement: Documentation covers install and project workflows
The system SHALL document how to run the script, how to choose global versus project installation, and how overwrite prompts behave.

#### Scenario: User follows global installation docs
- **WHEN** a user reads the package documentation
- **THEN** they can identify how to run the script for a global/user install

#### Scenario: User follows project-level installation docs
- **WHEN** a user wants skills installed only for one project
- **THEN** the documentation shows how to run the script for project-scope installation and how overwrite confirmation works
