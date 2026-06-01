## ADDED Requirements

### Requirement: Package SHALL include publishable Codex and OpenCode assets
The Macwdo distribution SHALL package the Codex skill tree from `.codex/skills/`, the OpenCode skill tree from `.opencode/skills/`, and the OpenCode slash commands from `.opencode/commands/`. The package MUST exclude transient OpenCode workspace files that are not runtime assets.

#### Scenario: Packaged assets are validated
- **WHEN** maintainers run package verification for the published bundle
- **THEN** the verification MUST confirm that every bundled Codex skill file, every bundled OpenCode skill file, and every bundled OpenCode command file is present in the tarball
- **AND** the verification MUST fail if transient `.opencode` workspace files are included instead of only the allowed asset directories

### Requirement: Installer SHALL support runtime target selection
The Macwdo installer SHALL let users install assets for `codex`, `opencode`, or `both` from one command surface in both the Node CLI and the shell installer.

#### Scenario: User installs both runtimes by default
- **WHEN** a user runs the installer without specifying a runtime target
- **THEN** the installer MUST plan and install both Codex and OpenCode assets

#### Scenario: User installs only one runtime
- **WHEN** a user selects `codex` or `opencode`
- **THEN** the installer MUST copy only the assets for that runtime
- **AND** it MUST NOT create directories for the other runtime

### Requirement: Installer SHALL resolve Codex and OpenCode destinations by scope
The installer SHALL support user and project scopes for each runtime and MUST write assets into runtime-appropriate locations.

#### Scenario: User scope installs use runtime-specific homes
- **WHEN** a user runs a user-scope install for `both`
- **THEN** Codex skills MUST be installed to `$CODEX_HOME/skills` when `CODEX_HOME` is set, otherwise `~/.codex/skills`
- **AND** OpenCode skills and commands MUST be installed under `${XDG_CONFIG_HOME:-~/.config}/opencode/`

#### Scenario: Project scope installs use project-local directories
- **WHEN** a user runs a project-scope install for `both`
- **THEN** Codex skills MUST be installed under `<project-root>/.codex/skills`
- **AND** OpenCode skills and commands MUST be installed under `<project-root>/.opencode/`

### Requirement: Installer SHALL preserve existing conflict safety for each runtime
The installer SHALL keep existing overwrite protections for every runtime target and MUST apply `--yes`, `--force`, and `--dry-run` behavior consistently across Codex and OpenCode assets.

#### Scenario: Dry-run reports runtime-specific actions
- **WHEN** a user runs the installer with `--dry-run`
- **THEN** the output MUST show the selected runtime target, the destination paths, detected conflicts, and planned actions for each affected asset group
- **AND** the installer MUST NOT write any Codex or OpenCode files

#### Scenario: Conflict handling stays non-destructive without force
- **WHEN** existing Codex or OpenCode assets conflict with the install plan and `--force` is not set
- **THEN** the installer MUST skip or prompt according to the current interactive and `--yes` rules
- **AND** it MUST overwrite conflicting assets only when overwrite is explicitly confirmed or `--force` is provided
