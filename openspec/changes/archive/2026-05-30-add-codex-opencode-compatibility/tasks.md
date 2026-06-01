## 1. Package And CLI Target Model

- [x] 1.1 Update package allowlists to ship `.opencode/skills/` and `.opencode/commands/` without shipping transient `.opencode` workspace files.
- [x] 1.2 Extend the Node CLI argument parsing and help text with runtime target selection for `codex`, `opencode`, and `both`.
- [x] 1.3 Refactor the Node installer planning logic so it can install Codex and OpenCode payload groups with runtime-specific destinations.

## 2. Installer Behavior

- [x] 2.1 Implement OpenCode user-scope and project-scope destination resolution in the Node CLI.
- [x] 2.2 Preserve `--yes`, `--force`, and `--dry-run` behavior across Codex and OpenCode payloads in the Node CLI.
- [x] 2.3 Update the shell installer to support runtime target selection and OpenCode destination handling.

## 3. Verification And Docs

- [x] 3.1 Extend package verification to validate bundled OpenCode skills and commands plus runtime-specific install targets.
- [x] 3.2 Update README usage, runtime targeting, and validation documentation for Codex and OpenCode compatibility.
- [x] 3.3 Run validation, confirm behavior, and mark the completed tasks in this change.
