## Context

The current compatibility entrypoint, `src/main.py`, supports only `check` for the Codex target. It loads canonical `.ai/agents` and `.ai/skills` through `src/compatibility/parsing.py`, then validates Codex metadata through `src/compatibility/codex.py`.

Codex user configuration lives under `$HOME/.codex`. Existing local config backups show Codex agent registration uses a root `[agents]` table for runtime settings and one `[agents.<name>]` table per agent with at least `description` and `config_file = "agents/<name>.toml"`. The active config may not contain `[agents]`, so installation must support both inserting a new agents section and updating an existing one.

## Goals / Non-Goals

**Goals:**

- Add an install command that derives Codex agent files from canonical `.ai/agents` assets.
- Write installed agent files under `$HOME/.codex/agents/`.
- Write generated private Mires bundles under `$HOME/.codex/mires/agents/<agent-name>/`.
- Copy each installed agent's canonical `AGENT.md` and referenced `.ai/skills` packages into that private bundle.
- Register each installed agent in `$HOME/.codex/config.toml` using Codex's `[agents.<name>]` table shape.
- Preserve unrelated user configuration and existing non-Mires agent registrations.
- Make repeated installs deterministic and idempotent.
- Provide a dry-run path for previewing destination files and config registrations.

**Non-Goals:**

- Do not make `$HOME/.codex/agents/` an authoring source.
- Do not install `.ai/skills` into global `$HOME/.codex/skills`.
- Do not support runtimes other than Codex.
- Do not remove user-owned agents unless an explicit uninstall operation is added by a future change.

## Decisions

### Add an explicit install operation

`src/main.py` will keep `check` as the default command and add an `install` command. The install command will run the same inventory loading and Codex validation before writing output, so invalid canonical assets cannot produce partial runtime files.

Alternative considered: make `check` also install. That would surprise maintainers who expect validation to be read-only.

### Derive one Codex config-layer TOML file plus one private bundle per canonical agent

The Codex adapter will render each `.ai/agents/<agent>/AGENT.md` plus `agents/openai.yaml` metadata into `$HOME/.codex/agents/<agent>.toml`. It will also generate `$HOME/.codex/mires/agents/<agent>/` as a private runtime bundle containing that agent's `AGENT.md`, runtime metadata, and the `.ai/skills/<skill>/` packages referenced by the agent.

The generated TOML must be a valid Codex config layer, using official keys such as `developer_instructions` and `skills.config`. It must not contain custom metadata fields such as `display_name`, `default_prompt`, `bundle_path`, `parent`, or `children`. The generated prompt should point at the private bundle path, not at `.ai`, and prompt lines should be wrapped at 131 characters for readability.

Private bundles must live outside `$HOME/.codex/agents/**` so Codex does not scan bundle metadata as agent role TOML. The canonical `.ai` tree remains the source of truth, but installed agents should be usable without reading repository-local `.ai` paths during runtime.

Alternative considered: copy `AGENT.md` files directly into `$HOME/.codex/agents/`. Codex config points at `.toml` files in existing local examples, so direct Markdown copies would not match discovered runtime conventions.

Alternative considered: install copied skill packages under `$HOME/.codex/skills`. That would make Mires support skills globally discoverable and risks loading or exposing too much context in unrelated Codex sessions. Agent-private bundles keep the references available only through the generated agent prompt.

### Patch only managed agent registrations in config.toml

Config mutation will be text-preserving. The installer will locate existing `[agents]` and `[agents.<name>]` tables, update or append only registrations for canonical Mires agent names, and leave unrelated tables and comments intact where possible. If `[agents]` is missing, the installer will append one with conservative defaults only when needed for agent registration.

Alternative considered: parse and reserialize the full TOML file. Python's standard library has read-only TOML support, and full reserialization would likely rewrite unrelated user formatting.

### Support a configurable Codex home

The command will default to `Path.home() / ".codex"` and accept an override such as `--codex-home` for tests and dry runs. This keeps tests isolated from the developer's real home directory and makes the install path safer to validate.

Alternative considered: hard-code `$HOME/.codex`. That would make automated validation risky and brittle.

## Risks / Trade-offs

- Config patching is format-sensitive -> Limit edits to well-defined `[agents]` and `[agents.<name>]` table boundaries, preserve unrelated text, and test missing, existing, and mixed agent sections.
- Existing user agent names may collide with canonical Mires agent names -> Treat canonical Mires names as managed registrations and update only those entries; document that same-name user agents are overwritten by install.
- Partial writes could leave config and files inconsistent -> Render all content first, validate it, then write agent files and config; use deterministic output and avoid deleting unrelated files.
- Codex agent TOML schema could evolve -> Keep rendering centralized in the Codex adapter and base the initial shape on discovered local Codex config conventions.
- Private bundles could grow stale after source changes -> Recreate each managed `$HOME/.codex/mires/agents/<agent>/` directory on install, and treat bundle contents as generated output only.

## Migration Plan

1. Add install rendering and config patching behind `src/main.py install --target codex`.
2. Add dry-run and Codex-home override options.
3. Add focused tests for rendering and config patching using temporary directories.
4. Document the install command and validation commands.
5. Rollback by removing generated `$HOME/.codex/agents/<agent>.toml` files, generated `$HOME/.codex/mires/agents/<agent>/` bundles, and their `[agents.<name>]` entries from Codex config.
