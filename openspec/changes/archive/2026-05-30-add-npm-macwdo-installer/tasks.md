## 1. Package Setup

- [x] 1.1 Add root npm package metadata for `@macwdo/macwdo`, including `name`, `version`, `description`, `license`, `engines`, `bin`, `files`, and script entries.
- [x] 1.2 Add the Node CLI entry point referenced by the `bin` field with a `#!/usr/bin/env node` shebang.
- [x] 1.3 Configure the package allowlist so CLI files, documentation, and `.codex/skills/**` are included in the npm tarball.
- [x] 1.4 Add package scripts for linting or syntax checks, package dry-run validation, and temporary install verification.

## 2. CLI Commands

- [x] 2.1 Implement `macwdo --help` with command descriptions and install scope options.
- [x] 2.2 Implement `macwdo --version` using the installed package metadata.
- [x] 2.3 Implement `macwdo list` to enumerate bundled skill names from the packaged `.codex/skills` directory.
- [x] 2.4 Implement argument parsing for `install`, `--scope`, `--project-root`, `--yes`, `--force`, and `--dry-run`.
- [x] 2.5 Return non-zero exit codes with clear messages for unknown commands, invalid flags, missing paths, and missing bundled skill assets.

## 3. Destination Resolution

- [x] 3.1 Resolve user-scope destination to `$CODEX_HOME/skills` when `CODEX_HOME` is set and otherwise `~/.codex/skills`.
- [x] 3.2 Resolve project-scope destination to `<project-root>/.codex/skills`.
- [x] 3.3 Default project scope to the current working directory when `--project-root` is omitted.
- [x] 3.4 Prompt for user versus project scope when `macwdo install` runs in an interactive terminal without `--scope`.
- [x] 3.5 Reject non-interactive installs that omit required scope input.

## 4. Install Behavior

- [x] 4.1 Discover every bundled skill directory under the packaged `.codex/skills` source.
- [x] 4.2 Recursively copy each skill directory to the resolved destination with relative paths preserved.
- [x] 4.3 Preserve nested `agents`, `references`, `scripts`, `assets`, and other package-local files during copy.
- [x] 4.4 Detect destination conflicts before writes and prompt to overwrite or skip each conflicting skill in interactive mode.
- [x] 4.5 Implement `--force` to overwrite conflicting destination skill directories without per-skill prompts.
- [x] 4.6 Implement `--yes` for non-destructive confirmations while still requiring `--force` for unattended overwrites.
- [x] 4.7 Implement `--dry-run` to print destination, selected skill count, conflicts, and planned copy actions without changing files.
- [x] 4.8 Print an installation summary with installed, overwritten, skipped, and destination counts.

## 5. Verification

- [x] 5.1 Add tests or scripts that install from `npm pack` output into a temporary directory.
- [x] 5.2 Verify `macwdo --help`, `macwdo --version`, and `macwdo list` from the packed package.
- [x] 5.3 Verify user-scope and project-scope destination resolution with temporary directories.
- [x] 5.4 Verify dry-run mode performs no filesystem writes.
- [x] 5.5 Verify conflict handling preserves existing skills unless overwrite is confirmed or `--force` is used.
- [x] 5.6 Verify every bundled `SKILL.md` and every `agents/openai.yaml` from the repository is present after installation.
- [x] 5.7 Run `npm pack --dry-run` and confirm package contents include the CLI, package metadata, documentation, all skills, and all subagent configs.

## 6. Documentation

- [x] 6.1 Update README with `npm install -g @macwdo/macwdo` and `macwdo install --scope user` usage.
- [x] 6.2 Document local usage through project dependencies, npm scripts, `npm exec`, or `npx`.
- [x] 6.3 Document the distinction between npm package install scope and Codex skill install scope.
- [x] 6.4 Document overwrite behavior, `--yes`, `--force`, and `--dry-run`.
- [x] 6.5 Document maintainer validation steps before publishing.
