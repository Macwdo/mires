## Context

This repository is a collection of local Codex skills under `.codex/skills/`. Consumers currently need to clone or copy repository contents manually, which makes reuse, updates, and project-specific installation inconsistent.

The requested distribution model is a single shell script that can be run from a cloned repository or a downloaded copy. The script should behave like a guided installer: choose global/user-level or project-level installation, confirm before overwriting, and copy the bundled skills into the selected Codex destination.

## Goals / Non-Goals

**Goals:**

- Provide a single shell installer that is easy to run from a clone or downloaded archive.
- Install all bundled skills by default.
- Support user-level and project-level install scopes.
- Prompt before overwriting existing skills.
- Resolve destinations consistently and show the target before writing.
- Keep installed skills identical to the repository's bundled `.codex/skills` content.

**Non-Goals:**

- Building a hosted registry service for skills.
- Introducing a package manager dependency for installation.
- Syncing skills automatically in the background after installation.
- Managing non-Codex editor or agent configuration outside the copied skill package files.

## Decisions

### Use a POSIX shell script

The installer will be a POSIX shell script so it can run in a plain clone, from a downloaded release, or from any machine that has a standard `sh` implementation. That keeps the entry point simple and avoids package-manager coupling.

Alternative considered: a Bun or Node CLI. That is better for richer argument parsing, but it adds a runtime dependency that the request explicitly avoids.

### Install from repository contents

The script will treat the repository's `.codex/skills/**` as the source of truth, enumerate bundled skill directories, and copy them to the destination. It may clone the repository if needed, but the install source remains the checked-in skills tree.

Alternative considered: download skills individually from GitHub. A full repository source is simpler and keeps the installed content aligned with a single revision.

### Prompt for install scope and overwrite behavior

The script will prompt the user to choose user/global scope or project scope before it writes files. If the destination already contains a skill directory, the script will ask whether to overwrite it or skip it.

Alternative considered: requiring flags only. Prompts are slower for automation, but they are a better fit for a one-off installer that should avoid accidental overwrites.

### Use explicit install scopes

The script will support user/global scope and project scope. User scope targets the user's Codex home, defaulting to `$CODEX_HOME/skills` when set and falling back to `~/.codex/skills`. Project scope targets `<project>/.codex/skills`, defaulting to the current working directory unless the user chooses a different project root.

Alternative considered: a single arbitrary destination prompt only. Scope-aware prompts are more understandable for the two install modes the user asked for.

## Risks / Trade-offs

- Shell portability issues -> Keep to POSIX `sh` features and standard utilities.
- Accidental overwrite of local skill edits -> Prompt before overwrite and default to skipping conflicts.
- Ambiguous project destination -> Print the resolved destination before writes.
- Copying large skill trees via shell -> Use standard file-copy commands and keep the script focused on orchestration rather than transformation.

## Migration Plan

1. Add the shell installer and documentation without changing existing skill directories.
2. Add checks or small tests for scope resolution, overwrite prompting, and copy behavior using temporary directories.
3. Verify the script works from a clean clone and from a downloaded copy.
4. Keep manual copy as a fallback path if users prefer not to run the installer.

## Open Questions

- Should the script support a `--yes` mode for non-interactive installs, or remain prompt-driven only?
- Should project-level installation write only to `.codex/skills`, or also offer to update local project guidance files?
- Should the script clone the repository itself when run from elsewhere, or assume the source tree is already present?
