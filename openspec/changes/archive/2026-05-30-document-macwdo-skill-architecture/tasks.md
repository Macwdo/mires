## 1. Architecture Guide

- [x] 1.1 Create `docs/macwdo-skill-architecture.md` explaining the repository layout across `.codex/skills`, `.opencode/skills`, `.opencode/commands`, `openspec/changes`, and agent config files.
- [x] 1.2 Document the Macwdo hierarchy roles: namespace entrypoint, explorer/router skills, leaf implementation skills, workflow skills, and agent-backed workflows.
- [x] 1.3 Add an evaluation framework for deciding whether new guidance belongs in an existing leaf, a new leaf, a router map, an OpenCode command, or an agent-backed workflow.
- [x] 1.4 Include a direct assessment of the current structure with strengths, risks, and recommended maintenance practices.

## 2. Discoverability

- [x] 2.1 Link the architecture guide from `README.md` without changing installer behavior or command documentation semantics.
- [x] 2.2 Keep `.codex/skills/macwdo/SKILL.md` as a compact runtime routing entrypoint rather than expanding it into long-form documentation.

## 3. Validation

- [x] 3.1 Verify the guide references only paths that exist in the current repository or are clearly marked as future options.
- [x] 3.2 Review the guide against representative skills such as `macwdo`, `macwdo-explorer`, `macwdo-python-django-explorer`, a leaf skill, and an OpenCode command.
- [x] 3.3 Run `git status --short` and confirm only intended documentation and OpenSpec files changed.
