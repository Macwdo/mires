## 1. Target Dispatch

- [x] 1.1 Refactor `src/main.py` to dispatch `check` and `install` operations by target instead of always calling Codex functions.
- [x] 1.2 Add `opencode` to supported target help text and keep unsupported target errors clear.
- [x] 1.3 Add an `--opencode-home` option defaulting to `~/.config/opencode` for OpenCode install output.

## 2. OpenCode Adapter

- [x] 2.1 Create `src/compatibility/opencode.py` with OpenCode validation, rendering, and install functions.
- [x] 2.2 Render each canonical agent as an OpenCode Markdown agent under `<opencode-home>/agents/<agent>.md` with valid YAML front matter and generated instructions.
- [x] 2.3 Install canonical skill packages under `<opencode-home>/skills/<skill>/SKILL.md` with valid OpenCode skill front matter and copied references.
- [x] 2.4 Ensure generated OpenCode files do not contain repository-local `.ai/` paths and point users back to canonical `.ai` source for edits.
- [x] 2.5 Support OpenCode dry-run output without creating the OpenCode home directory.

## 3. Tests

- [x] 3.1 Add unit tests for OpenCode agent rendering and skill package rendering.
- [x] 3.2 Add install command tests for `--target opencode` using an alternate OpenCode home.
- [x] 3.3 Add a dry-run test proving `--target opencode --dry-run` writes no files.
- [x] 3.4 Add target dispatch coverage proving Codex still works and unsupported targets still fail clearly.

## 4. Documentation And Verification

- [x] 4.1 Update README compatibility and install instructions to document both Codex and OpenCode targets.
- [x] 4.2 Update `scripts/verify_agent_first_surface.py` to run both compatibility checks and allow intentional OpenCode support references.
- [x] 4.3 Keep verification rejecting committed generated `.opencode` runtime output and duplicate runtime source trees.

## 5. Validation

- [x] 5.1 Run the OpenCode compatibility check with `python3 src/main.py --target opencode`.
- [x] 5.2 Run the Codex compatibility check with `python3 src/main.py --target codex`.
- [x] 5.3 Run the installer tests for Codex and OpenCode.
- [x] 5.4 Run `python3 scripts/verify_agent_first_surface.py`.
