## Why

Macwdo skills and agent configs currently live in this repository, but users still need a clone, downloaded source, or shell script to install them. Publishing an npm CLI package as `@macwdo/macwdo` would make setup match familiar tool flows such as `npm install -g @macwdo/macwdo`, while still letting users choose whether skills are installed for one project or for their user-level Codex environment.

## What Changes

- Add a publishable npm package named `@macwdo/macwdo`.
- Expose a `macwdo` CLI command through npm's package `bin` mechanism.
- Add an install command that copies every bundled skill package from `.codex/skills/**`, including nested `agents`, `references`, `scripts`, and `assets` files.
- Support both user/global and project/local skill installation scopes through explicit CLI options and an interactive fallback.
- Keep npm package installation scope separate from Codex skill installation scope: `npm install -g` controls CLI availability, while `macwdo install --scope user|project` controls where skills are copied.
- Document global npm installation, local npm usage, install scope selection, overwrite handling, and validation commands.

## Capabilities

### New Capabilities

- `npm-macwdo-installer`: Defines the npm package, `macwdo` CLI command, bundled skill asset installation behavior, local/global scope options, and publish validation.

### Modified Capabilities

- None.

## Impact

- Adds Node/npm package metadata, CLI source files, and packaging configuration.
- Adds installer logic that reads bundled `.codex/skills/**` content from the installed npm package and writes it to user-level or project-level Codex skill directories.
- Updates documentation for `npm install -g @macwdo/macwdo`, local usage through project dependencies or `npx`, and scope-specific skill installation.
- Adds packaging and installer verification, including `npm pack --dry-run` checks and temporary-directory install tests.
