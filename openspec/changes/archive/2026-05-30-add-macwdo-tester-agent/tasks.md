## 1. Add Unified Tester Skill

- [x] 1.1 Create `.codex/skills/macwdo-tester/SKILL.md` with workflow-focused guidance for local app verification.
- [x] 1.2 Include the consolidated sequence: inspect context, validate linked worktree when applicable, prepare portless, run routed dev server, verify with agent-browser, report and clean up.
- [x] 1.3 Reference `portless` and `agent-browser` as source skills for command-level details.

## 2. Add Tester Agent Configuration

- [x] 2.1 Create `.codex/skills/macwdo-tester/agents/openai.yaml`.
- [x] 2.2 Set display name to `Macwdo Tester` and default prompt to use `macwdo-tester`, `portless`, and `agent-browser`.

## 3. Consolidate Legacy Agent Testing Skills

- [x] 3.1 Decide whether old `macwdo-agent-testing-*` directories should be removed or converted to compatibility redirects.
- [x] 3.2 Apply the chosen migration so old testing skills do not compete with `macwdo-tester` in discovery.
- [x] 3.3 Remove or update old `macwdo-agent-testing-*` agent configs as needed.

## 4. Update Macwdo Routers

- [x] 4.1 Update `.codex/skills/macwdo/SKILL.md` so agent testing maps to `macwdo-tester`.
- [x] 4.2 Update `.codex/skills/macwdo-explorer/SKILL.md` so agent testing maps to `macwdo-tester`.

## 5. Validate

- [x] 5.1 Validate YAML for all changed `agents/openai.yaml` files.
- [x] 5.2 Check referenced paths in changed `SKILL.md` files.
- [x] 5.3 Run `openspec validate add-macwdo-tester-agent`.
- [x] 5.4 Run `openspec status --change add-macwdo-tester-agent` and confirm artifacts are complete.
