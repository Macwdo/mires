## 1. Command Surface

- [x] 1.1 Extend `src/main.py` to support `check` and `install` commands while keeping `check` as the default.
- [x] 1.2 Add install options for `--target codex`, `--codex-home`, and `--dry-run`.
- [x] 1.3 Ensure install runs inventory loading and Codex validation before writing any files.

## 2. Codex Agent Rendering

- [x] 2.1 Add Codex adapter functions that render each canonical agent into deterministic `<agent-name>.toml` content.
- [x] 2.2 Include agent description, default prompt, and source-derived metadata from `.ai/agents/<agent-name>/AGENT.md` and `agents/openai.yaml`.
- [x] 2.3 Write rendered files to `<codex-home>/agents/<agent-name>.toml`, creating the agents directory when needed.

## 3. Codex Config Registration

- [x] 3.1 Implement text-preserving config patching for missing and existing `[agents]` sections.
- [x] 3.2 Add or update managed `[agents.<agent-name>]` tables with `description` and `config_file = "agents/<agent-name>.toml"`.
- [x] 3.3 Preserve unrelated config content, root `[agents]` settings, and non-Mires `[agents.<name>]` registrations.
- [x] 3.4 Make repeated installs idempotent with no duplicate registrations.

## 4. Safety and Reporting

- [x] 4.1 Implement dry-run reporting that lists files and config registrations without writing.
- [x] 4.2 Render and validate all planned output before writing to avoid partial installs when canonical assets are invalid.
- [x] 4.3 Print installed agent count and Codex home on success.

## 5. Validation

- [x] 5.1 Add focused tests for agent rendering using sample canonical agent metadata.
- [x] 5.2 Add focused tests for config patching with no `[agents]`, existing `[agents]`, existing managed entries, and unrelated non-Mires agents.
- [x] 5.3 Add command-level tests or scripted validation using a temporary `--codex-home`.
- [x] 5.4 Run `python3 scripts/verify_agent_first_surface.py` and `python3 src/main.py --target codex`.

## 6. Documentation

- [x] 6.1 Document the Codex install command, dry-run option, and alternate Codex home option.
- [x] 6.2 Document that `.ai/agents` remains the canonical source and `$HOME/.codex/agents` is generated runtime output.

## 7. Private Agent Bundles

- [x] 7.1 Update generated agent TOML to point prompts at `$HOME/.codex/agents/mires/<agent-name>/` instead of `.ai` paths.
- [x] 7.2 Copy each installed agent's `AGENT.md` and `agents/openai.yaml` into its private bundle.
- [x] 7.3 Detect each agent's referenced `skills/<skill-name>` packages and copy them into the private bundle.
- [x] 7.4 Ensure Mires skill packages are not copied to global `$HOME/.codex/skills`.
- [x] 7.5 Refresh managed private bundles idempotently so stale generated files are removed on reinstall.
- [x] 7.6 Add tests for private bundle rendering, skill copying, no `.ai` runtime pointers, and no global skill writes.
- [x] 7.7 Reinstall the agents into `$HOME/.codex` with the private bundle layout.

## 8. Codex Schema Compatibility

- [x] 8.1 Move private bundles from `$HOME/.codex/agents/mires/<agent-name>/` to `$HOME/.codex/mires/agents/<agent-name>/`.
- [x] 8.2 Render agent role files as valid Codex config layers using official fields only.
- [x] 8.3 Replace custom prompt fields with improved `developer_instructions`.
- [x] 8.4 Wrap generated developer-instruction lines at 131 characters.
- [x] 8.5 Stop writing TOML metadata files under nested `$HOME/.codex/agents/**` directories.
- [x] 8.6 Add tests that generated role files have no unsupported fields and no nested agent TOML files exist.
- [x] 8.7 Reinstall the agents and verify Codex no longer reports malformed agent role definitions.
