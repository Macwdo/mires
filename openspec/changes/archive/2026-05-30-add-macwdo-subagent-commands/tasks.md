## 1. OpenCode Assets

- [x] 1.1 Create `.opencode/skills/macwdo-tester/SKILL.md` by adapting the existing Codex tester workflow to OpenCode skill format.
- [x] 1.2 Create `.opencode/skills/macwdo-reviewer/SKILL.md` by adapting the existing Codex reviewer workflow to OpenCode skill format.
- [x] 1.3 Create `.opencode/commands/macwdo-tester.md` as a thin OpenCode entrypoint that routes to the `macwdo-tester` skill.
- [x] 1.4 Create `.opencode/commands/macwdo-reviewer.md` as a thin OpenCode entrypoint that routes to the `macwdo-reviewer` skill.

## 2. Packaging And Docs

- [x] 2.1 Update documentation to mention the new OpenCode tester and reviewer commands and their installability through `--target opencode|both`.
- [x] 2.2 Ensure any package metadata or listing behavior still accurately describes the bundled Codex agents and OpenCode commands after the new assets are added.

## 3. Validation

- [x] 3.1 Run package validation and confirm the new OpenCode assets are bundled and install correctly.
- [x] 3.2 Mark the completed tasks in this change after validation passes.
