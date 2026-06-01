## Context

This repository already ships Codex-first Macwdo entrypoints such as `macwdo-tester` and `macwdo-reviewer` under `.codex/skills/<name>/`, including `agents/openai.yaml` configs. The installer and package flow were recently extended to support both Codex and OpenCode assets, but the OpenCode payload still only contains the OpenSpec helper skills and slash commands.

The user request is specifically about making `macwdo-tester` and `macwdo-reviewer` available as installable command and agent entrypoints across runtimes. In practice, that means preserving the existing Codex skill-plus-agent setup and adding the missing OpenCode equivalents as skills and slash commands.

## Goals / Non-Goals

**Goals:**

- Add OpenCode skill entrypoints for `macwdo-tester` and `macwdo-reviewer`.
- Add OpenCode slash commands that route into those skills.
- Keep the current Codex `agents/openai.yaml` entrypoints unchanged.
- Ensure the existing packaging, listing, and installation flows include the new OpenCode assets.
- Document the new OpenCode command entrypoints for global and project installs.

**Non-Goals:**

- Redesigning the tester or reviewer workflows.
- Introducing new Codex agent packages beyond the existing `macwdo-tester` and `macwdo-reviewer` directories.
- Adding a new installer target or changing destination paths.
- Creating OpenCode versions of every Macwdo skill in this change.

## Decisions

### Mirror the existing Codex skill names in OpenCode

Create `.opencode/skills/macwdo-tester/SKILL.md` and `.opencode/skills/macwdo-reviewer/SKILL.md` so the same names work across runtimes.

Alternative considered: use OpenCode-specific names such as `macwdo-test` or `macwdo-review`. That would make cross-runtime documentation and user expectations less consistent.

### Keep slash commands thin and skill-driven

Create `.opencode/commands/macwdo-tester.md` and `.opencode/commands/macwdo-reviewer.md` as thin entrypoints that tell OpenCode to use the matching skill. The detailed workflows remain in the skill files.

Alternative considered: duplicate the full tester and reviewer instructions in the command markdown. That would create two sources of truth per workflow and increase drift risk.

### Reuse the current Codex workflow content with OpenCode-compatible front matter

The new OpenCode skill files should closely mirror the existing Codex `SKILL.md` content so runtime behavior stays aligned, while adopting the metadata shape already used by `.opencode/skills/*/SKILL.md`.

Alternative considered: write shorter OpenCode-only summaries. That would make the OpenCode workflows meaningfully less capable than the Codex ones.

### Rely on the existing installer architecture and extend docs/verification only where needed

The current package allowlist, CLI list/install logic, and verification script already enumerate `.opencode/skills/**` and `.opencode/commands/**` dynamically. This change should therefore focus on adding the new assets, plus any README or verification adjustments needed to make the new entrypoints explicit.

Alternative considered: refactor installer logic again. That adds risk without solving a new problem for this scope.

## Risks / Trade-offs

- Skill text will exist in both Codex and OpenCode trees -> Keep the OpenCode versions closely aligned to the Codex source skills and keep the command files minimal.
- Command naming could be slightly awkward with long slash command names -> Prefer exact parity with the established skill names over shorter but inconsistent aliases.
- Documentation could overstate broader runtime parity -> Limit README updates to `macwdo-tester` and `macwdo-reviewer` specifically.

## Migration Plan

1. Add the OpenCode `macwdo-tester` and `macwdo-reviewer` skill directories.
2. Add matching OpenCode slash command files.
3. Update README examples and notes for the new commands.
4. Run package verification to confirm the new assets are bundled and installable.

## Open Questions

- None.
