## 1. Package Setup

- [x] 1.1 Add the shell installer script and mark it executable.
- [x] 1.2 Add any minimal helper script or shared shell functions needed for portability.
- [x] 1.3 Document the repository source layout expected by the installer, including `.codex/skills/**`.

## 2. Installer Flow

- [x] 2.1 Prompt for global/user-level versus project-level installation.
- [x] 2.2 Resolve the default destination for each scope.
- [x] 2.3 Prompt for or accept a project root when project scope is chosen.
- [x] 2.4 Detect whether the source repository is available locally and fail with a clear message if not.

## 3. Configuration

- [x] 3.1 Define the interactive confirmation prompts for overwrite and install scope.
- [x] 3.2 Add a non-interactive `--yes` or equivalent mode only if required for automation.
- [x] 3.3 Validate destination paths and fail before writes when required inputs are missing or invalid.

## 4. Installation Behavior

- [x] 4.1 Implement recursive copying of `.codex/skills/**` to the chosen destination.
- [x] 4.2 Implement overwrite prompts for existing skill directories.
- [x] 4.3 Implement skip behavior when overwrite is declined.
- [x] 4.4 Ensure copied skills preserve relative paths and file permissions where practical.

## 5. Tests

- [x] 5.1 Add checks or tests for user-scope and project-scope destination resolution.
- [x] 5.2 Add checks or tests for overwrite prompts and skipped conflicts.
- [x] 5.3 Add checks or tests for recursive copy behavior from `.codex/skills/**`.
- [x] 5.4 Add checks or tests for missing-source and invalid-path failures.

## 6. Documentation and Verification

- [x] 6.1 Document how to run the installer from a clone or downloaded copy.
- [x] 6.2 Document how to choose global/user versus project installation.
- [x] 6.3 Document overwrite confirmation behavior and the resulting file locations.
- [x] 6.4 Verify the script works in a clean test directory before marking the change complete.
