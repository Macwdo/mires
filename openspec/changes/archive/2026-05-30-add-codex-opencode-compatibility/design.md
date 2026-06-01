## Context

The current package and installer flow were built around Codex only. The packaged payload is sourced from `.codex/skills/`, the Node CLI resolves only `.codex` destinations, the shell installer copies only `.codex/skills`, and the verification script only checks Codex package contents and install targets.

This repository also contains OpenCode assets under `.opencode/skills/` and `.opencode/commands/`. Those assets are structurally different from the Codex payload because OpenCode needs both skills and slash-command markdown files, and the `.opencode/` workspace also contains transient files such as `node_modules/` and local package metadata that must not be published.

## Goals / Non-Goals

**Goals:**

- Keep the existing Codex installer behavior working.
- Add first-class OpenCode installation support in the npm CLI and shell installer.
- Let users choose `codex`, `opencode`, or `both` from one installer flow.
- Package only the OpenCode assets that should ship: `.opencode/skills/**` and `.opencode/commands/**`.
- Validate package contents and install results for both runtimes.

**Non-Goals:**

- Packaging the entire `.opencode/` directory.
- Managing OpenCode plugins, `node_modules`, or lockfiles.
- Renaming existing skills or commands.
- Reworking the CLI into a different command structure beyond the minimum needed target support.

## Decisions

### Introduce explicit install targets

Add `--target codex|opencode|both` to the Node CLI and shell installer. Default to `both` when no target is provided so a fresh install from this package makes the repo usable with either runtime without an extra command.

Alternative considered: infer the target from the working tree or installed tools. That is harder to explain and creates surprising partial installs.

### Model install payloads by runtime

Treat the packaged content as two runtime payloads:

- Codex: `.codex/skills/**`
- OpenCode: `.opencode/skills/**` and `.opencode/commands/**`

The Node CLI should build an install plan from these payload groups instead of assuming one source directory and one destination root.

Alternative considered: flatten everything into a single generic asset copy list. Grouping by runtime keeps help text, summary output, verification, and destination resolution easier to reason about.

### Keep current Codex destinations and add explicit OpenCode destinations

Continue resolving Codex targets as:

- user: `$CODEX_HOME/skills` or `~/.codex/skills`
- project: `<project-root>/.codex/skills`

Resolve OpenCode targets as:

- user skills: `${XDG_CONFIG_HOME:-~/.config}/opencode/skills`
- user commands: `${XDG_CONFIG_HOME:-~/.config}/opencode/commands`
- project skills: `<project-root>/.opencode/skills`
- project commands: `<project-root>/.opencode/commands`

Alternative considered: install OpenCode user assets under `~/.opencode`. The repository layout uses `.opencode` for project-local files, while the observed user-level skill location in this environment is under `~/.config/opencode`, so the installer should align to that split.

### Exclude transient OpenCode workspace files from the npm package

Extend `package.json` `files` to include only the publishable OpenCode asset directories. Do not include `.opencode/node_modules`, `.opencode/package.json`, `.opencode/package-lock.json`, or `.opencode/.gitignore`.

Alternative considered: include `.opencode/` and rely on ignore rules. Explicit allowlisting is safer for a public package.

### Extend verification around runtime-specific expectations

The verification script should assert that the packed tarball includes all Codex skills, OpenCode skills, and OpenCode commands, and that installation writes them to the expected user and project targets for the chosen runtime.

Alternative considered: keep only smoke tests. The package already has strong verification coverage, so the incremental change should stay at the same rigor level.

## Risks / Trade-offs

- User-level OpenCode path could vary across environments -> Prefer `XDG_CONFIG_HOME` when set, otherwise fall back to `~/.config/opencode`.
- Defaulting to `both` increases install volume -> The repo is a bundled skill pack, and the default reduces confusion for users who want compatibility out of the box.
- More installer branches increase maintenance cost -> Reuse shared copy and conflict logic where possible and keep the runtime split data-driven.
- Verification becomes more complex -> Keep expected files grouped by runtime so failures are localized and readable.

## Migration Plan

1. Create the change spec and tasks for the combined runtime installer.
2. Update package allowlists and CLI installer target model.
3. Update the shell installer with matching runtime selection and OpenCode destinations.
4. Extend verification for OpenCode packaged assets and install targets.
5. Update README usage and validation documentation.

## Open Questions

- None.
