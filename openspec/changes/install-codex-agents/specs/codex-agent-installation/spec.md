## ADDED Requirements

### Requirement: Codex agent install command
The system SHALL expose a Codex install operation through the Python compatibility entrypoint.

#### Scenario: Maintainer installs Codex agents
- **WHEN** a maintainer runs the compatibility entrypoint with the install command for the Codex target
- **THEN** the workflow loads canonical `.ai` assets
- **AND** it validates Codex compatibility before writing runtime output
- **AND** it reports the installed agent count and destination Codex home

#### Scenario: Invalid canonical assets are discovered
- **WHEN** the install command discovers missing front matter, missing runtime metadata, or invalid Codex metadata
- **THEN** it exits unsuccessfully
- **AND** it reports the affected path and validation reason
- **AND** it does not create partial Codex agent output

### Requirement: Canonical agents are rendered into Codex agent files
The system SHALL render canonical `.ai/agents/<agent-name>/` assets into Codex agent files under `$HOME/.codex/agents/`.

#### Scenario: Agent file is installed
- **WHEN** a canonical agent has valid `AGENT.md` front matter and Codex metadata
- **THEN** the install command writes a derived agent file to `$HOME/.codex/agents/<agent-name>.toml`
- **AND** the derived file is a valid Codex config layer with no unsupported custom fields
- **AND** the derived file contains improved `developer_instructions` based on canonical metadata
- **AND** each developer-instruction line is at most 131 characters
- **AND** the derived file points runtime instructions at `$HOME/.codex/mires/agents/<agent-name>/`
- **AND** the derived file does not point runtime instructions at repository-local `.ai` paths
- **AND** the canonical `.ai/agents` source remains unchanged

#### Scenario: Install is repeated
- **WHEN** the install command is run multiple times with unchanged canonical assets
- **THEN** the generated Codex agent files remain deterministic
- **AND** the generated private Mires bundles remain deterministic
- **AND** the command does not create duplicate files or duplicate config entries

### Requirement: Agent references are installed as private bundles
The system SHALL install per-agent Mires reference bundles under `$HOME/.codex/mires/agents/` instead of global Codex skills.

#### Scenario: Agent bundle is installed
- **WHEN** a canonical agent is installed
- **THEN** the install command writes the agent's canonical `AGENT.md` to `$HOME/.codex/mires/agents/<agent-name>/AGENT.md`
- **AND** it writes the agent's runtime metadata to `$HOME/.codex/mires/agents/<agent-name>/agents/openai.yaml`
- **AND** it writes each `.ai/skills/<skill-name>/` package referenced by that agent to `$HOME/.codex/mires/agents/<agent-name>/skills/<skill-name>/`
- **AND** generated bundle files rewrite repository-local `.ai` references to bundle-local references
- **AND** generated bundle metadata does not create TOML files under `$HOME/.codex/agents/**`

#### Scenario: Global Codex skills are not polluted
- **WHEN** canonical Mires skill packages are copied for an installed agent
- **THEN** they are copied only under the agent's private bundle
- **AND** the install command does not write Mires skill packages to `$HOME/.codex/skills/`

#### Scenario: Bundle is refreshed
- **WHEN** an install is repeated after canonical agent or skill content changes
- **THEN** the command refreshes the managed private bundle for that agent
- **AND** stale files from the previous generated bundle are removed

### Requirement: Codex config registers installed agents
The system SHALL register installed agents in `$HOME/.codex/config.toml` using Codex agent tables.

#### Scenario: Config has an existing agents section
- **WHEN** `$HOME/.codex/config.toml` contains an `[agents]` section
- **THEN** the install command preserves existing `[agents]` settings
- **AND** it adds or updates `[agents.<agent-name>]` tables for canonical Mires agents
- **AND** each installed agent registration points `config_file` at `agents/<agent-name>.toml`

#### Scenario: Config has no agents section
- **WHEN** `$HOME/.codex/config.toml` does not contain an `[agents]` section
- **THEN** the install command creates an `[agents]` section
- **AND** it adds `[agents.<agent-name>]` tables for canonical Mires agents
- **AND** it preserves unrelated existing config content

#### Scenario: Non-Mires agent registrations exist
- **WHEN** `$HOME/.codex/config.toml` contains `[agents.<name>]` tables that are not generated from current canonical Mires agents
- **THEN** the install command preserves those registrations
- **AND** it does not rewrite their descriptions or config file paths

### Requirement: Install path supports dry-run and isolated Codex home
The system SHALL support previewing install changes and targeting an alternate Codex home.

#### Scenario: Dry run is requested
- **WHEN** a maintainer runs the install command with dry-run enabled
- **THEN** the workflow reports agent files and config registrations it would create or update
- **AND** it does not write files

#### Scenario: Alternate Codex home is provided
- **WHEN** a maintainer provides an alternate Codex home path
- **THEN** the install command reads and writes `.codex` files relative to that path
- **AND** it does not touch the user's default `$HOME/.codex` directory
