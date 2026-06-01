## Context

This repository packages Codex skills, OpenCode skills and commands, installer scripts, and a Node CLI for distributing local agent runtime guidance. The active source tree currently uses Macwdo as the product namespace across npm package metadata, CLI command names, skill directory names, YAML front matter, agent prompts, documentation, and verification scripts.

The requested rename is a full active namespace migration to Mires. Historical OpenSpec archives are excluded because they describe past changes and should remain stable records.

## Goals / Non-Goals

**Goals:**

- Rename the active npm package and CLI command to `@mires/mires` and `mires`.
- Rename active Codex and OpenCode skill IDs, directories, slash commands, metadata, and cross-references from `macwdo` to `mires`.
- Update agent configs, documentation, installer examples, and package verification so published artifacts install and verify Mires assets.
- Ensure no stale product-source `macwdo`, `Macwdo`, or `@macwdo` references remain outside OpenSpec change records.

**Non-Goals:**

- Rewriting archived OpenSpec change history under `openspec/changes/archive/**`.
- Providing backward-compatible `macwdo` package aliases, CLI aliases, or duplicate skill IDs.
- Changing the behavior of the installer beyond the namespace rename.

## Decisions

### Use a breaking rename without compatibility aliases

Rename the package, CLI executable, source file names, skill IDs, and command names directly to Mires. This keeps the distribution clean and prevents users from installing duplicate Macwdo and Mires skill packages that contain the same guidance.

Alternative considered: keep `macwdo` as a compatibility binary and duplicate old skill IDs. That would reduce migration friction, but it contradicts the requested full rename and increases maintenance burden.

### Rename directories and front matter together

Codex and OpenCode skill package names are represented both by directory names and by `name:` front matter in `SKILL.md`. Rename both in the same task so runtime discovery and documentation stay consistent.

Alternative considered: update text first and rename directories later. That creates an intermediate state where skills can reference IDs that do not exist on disk.

### Exclude archived OpenSpec history from automated replacement

Archived changes remain historical records. Validation should search active product source while ignoring `openspec/changes/**`, so historical and in-progress change records can describe the rename without blocking completion.

Alternative considered: rewrite every archived reference. The user explicitly declined that, and changing archived artifacts would blur historical provenance.

### Validate with package checks and targeted search

Run the existing Node syntax/package verification after the rename, then run a repository search excluding archives to catch active stale names.

Alternative considered: rely only on grep. Package verification is needed because executable paths and package allowlists can break after file renames.

## Risks / Trade-offs

- Existing users of the Macwdo package or CLI will need to reinstall and update commands -> Document the new `@mires/mires` and `mires` names clearly.
- Directory renames may be hard to review in a dirty working tree -> Keep edits mechanical and avoid touching unrelated files.
- Package verification may fail if npm pack still references old file names -> Update package scripts, bin mappings, and verification expected paths together.
- Active references can hide in generated docs or agent prompts -> Run a final search for `macwdo`, `Macwdo`, and `@macwdo` excluding OpenSpec change records.
