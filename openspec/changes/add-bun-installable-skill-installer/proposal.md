## Why

The repository currently stores useful Codex skills, but installing them requires manual copying or direct repository access. A single shell installer would make setup repeatable with a simple download-and-run flow while still letting the user choose between global and project-level installation.

## What Changes

- Add a single POSIX shell installer script that can be run from a clone or from a downloaded copy of the repository.
- Prompt the user to choose global/user-level installation or project-level installation.
- Ask before overwriting existing skills and only replace files when the user confirms.
- Install all bundled skills by default, with clear handling for target destination paths.
- Document how to run the script, what it installs, and where files are written.

## Capabilities

### New Capabilities

- `shell-skill-installer`: Defines a one-script installation flow for bundled Codex skills with user confirmation and install scope selection.

### Modified Capabilities

- None.

## Impact

- Adds a shell script, supporting helper logic if needed, and documentation for running it.
- Adds install/copy logic that reads `.codex/skills/` and writes selected skills to user-level or project-level Codex skill directories.
- Adds documentation for installing from a clone or downloaded source and for overwrite confirmation behavior.
- May introduce lightweight checks for destination resolution and copy behavior.
