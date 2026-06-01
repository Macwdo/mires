## Context

This repository is a collection of Codex skills under `.codex/skills/`. There are currently 95 skill packages, and some of those packages include subagent configuration files under `agents/openai.yaml`. The existing `install.sh` copies skills from a clone or downloaded source tree, but it does not provide a registry-installable CLI package.

The requested distribution model is `npm install -g @macwdo/macwdo`, similar to CLI tools such as OpenSpec. npm supports executable package entry points through the `bin` field and links those executables differently for global and local package installs. npm also supports checking publish contents with `npm pack --dry-run`, which is important because the bundled source lives under a hidden `.codex` directory.

## Goals / Non-Goals

**Goals:**

- Publish this repository as an npm package named `@macwdo/macwdo`.
- Provide a `macwdo` executable command after global installation.
- Support local package installation and local CLI invocation through `npm exec`, `npx`, or npm scripts.
- Install all bundled skills, including nested subagent configs and supporting files.
- Let users choose user/global Codex installation or project-local Codex installation.
- Make install behavior automatable through flags and safe by default in interactive mode.
- Validate that the npm tarball contains all required skills and subagent files.

**Non-Goals:**

- Creating a hosted skill registry or remote update service.
- Installing skills automatically from an npm lifecycle hook.
- Selecting a subset of skills in the first version.
- Managing secrets, Codex runtime configuration, or non-Codex agent configuration outside copied skill packages.
- Replacing `install.sh` immediately; it can remain as a source-install fallback.

## Decisions

### Use a root npm package with a `macwdo` bin

Add a root `package.json` for `@macwdo/macwdo` with a `bin` mapping from `macwdo` to a Node CLI entry point such as `bin/macwdo.js`. The bin script starts with `#!/usr/bin/env node` so npm can link it correctly across global and local installs.

Alternative considered: keep only `install.sh`. The shell script is useful from a clone, but it does not satisfy registry installation through `npm install -g @macwdo/macwdo`.

### Separate npm installation scope from Codex asset installation scope

`npm install -g @macwdo/macwdo` controls where the CLI package is installed and whether `macwdo` is on the user's PATH. `macwdo install --scope user|project` controls where skills are copied. The CLI should also prompt for scope when `--scope` is omitted in an interactive terminal.

Alternative considered: use npm `postinstall` to copy skills immediately. That hides filesystem writes inside package installation, makes project versus user scope ambiguous, and is hard to run safely in CI or package manager environments that disable lifecycle scripts.

### Bundle `.codex/skills/**` inside the npm package

Use the npm `files` field to include the CLI files, documentation, and `.codex/skills/**`. The implementation must validate package contents with `npm pack --dry-run` and by installing from a generated tarball into a temporary project.

Alternative considered: download skills from GitHub at CLI runtime. Bundling the checked-in skills keeps installation deterministic for each npm package version and avoids network dependencies after npm has installed the package.

### Copy whole skill directories without transforming files

The installer treats each directory under bundled `.codex/skills/` as an atomic skill package and recursively copies it to the destination. This preserves `SKILL.md`, `references`, `agents`, `scripts`, `assets`, and future package-local files without maintaining a separate manifest.

Alternative considered: generate a manifest of files. A manifest can help auditing later, but it adds maintenance overhead while the current repository already defines skill boundaries by directory.

### Support explicit, scriptable install flags

The first CLI surface should be:

- `macwdo install`
- `macwdo install --scope user`
- `macwdo install --scope project --project-root <path>`
- `macwdo install --yes`
- `macwdo install --force`
- `macwdo install --dry-run`
- `macwdo list`
- `macwdo --version`
- `macwdo --help`

`--yes` answers non-destructive confirmations, while `--force` is required to replace existing skill directories without per-skill prompts. `--dry-run` reports planned writes without changing files.

Alternative considered: only an interactive command. That is easier to build, but harder to validate and automate.

### Use Node standard library first

Implement the CLI with Node's standard library for argument parsing, path resolution, terminal prompts, and recursive copying. Add a dependency only if the implementation becomes materially clearer or safer.

Alternative considered: use a full CLI framework. That is reasonable later, but initial commands are small enough to keep dependency risk low.

## Risks / Trade-offs

- Hidden package assets are omitted from the tarball -> Include `.codex/skills/**` explicitly in `package.json` and verify with `npm pack --dry-run`.
- Global npm install succeeds but `macwdo` is unavailable -> Document npm global bin path behavior and validate the generated package's `bin` mapping.
- Users confuse npm global install with user-level Codex install -> Documentation and CLI output must distinguish CLI package installation from Codex skill installation.
- Existing local skill edits are overwritten -> Default to prompting or skipping conflicts; require `--force` for unattended replacement.
- Windows path and executable behavior differs from Unix -> Use Node path APIs and test CLI execution from the packed package on the supported platforms available locally.
- Published package accidentally includes unrelated repo files -> Use `files` as an allowlist and validate tarball contents before publishing.

## Migration Plan

1. Add package metadata, CLI source, and package file allowlist without changing existing skill directories.
2. Implement read-only commands (`--help`, `--version`, `list`) before write commands.
3. Implement `install` with dry-run, explicit scope flags, destination resolution, conflict detection, and copy behavior.
4. Add temporary-directory tests that install from `npm pack` output and verify all bundled skills and agent files are copied.
5. Update README with global and local npm usage, install scopes, and publish verification.
6. Keep `install.sh` documented as a clone/download fallback until the npm path is proven.

## Open Questions

- What npm account or organization will own the `@macwdo` scope?
- Should the package require the same Node.js baseline as OpenSpec, or use the lowest maintained Node.js version that supports the implementation?
- Should the first version publish publicly or remain private until installation is tested from a real npm registry install?
