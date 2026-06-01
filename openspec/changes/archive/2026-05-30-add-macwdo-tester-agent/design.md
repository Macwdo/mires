## Context

Macwdo currently has a small agent-testing family:

- `macwdo-agent-testing-explorer` routes to testing leaves.
- `macwdo-agent-testing-portless` defines linked-worktree and routed URL rules.
- `macwdo-agent-testing-browser-verification` defines the browser verification loop.
- `macwdo-agent-testing-reporting` defines the final pass/fail report.

The practical testing workflow also needs the personal `portless` and `agent-browser` skills, which contain command-level reference material. The new `macwdo-tester` should be the single Macwdo agent entrypoint that composes these concerns in the correct order.

## Goals / Non-Goals

**Goals:**

- Add `macwdo-tester` as the canonical testing skill and agent.
- Preserve the current testing rules: linked-worktree awareness, no raw localhost guessing, portless routed URLs, snapshot-driven browser interaction, and concise reporting.
- Update Macwdo routers so users and subagents discover `macwdo-tester` first.
- Reduce agent surface area by replacing several narrow testing agents with one cohesive tester agent.

**Non-Goals:**

- Reimplement `agent-browser` or `portless` CLI documentation inside Macwdo.
- Change the behavior of `agent-browser` or `portless`.
- Add a test harness, executable scripts, or generated browser artifacts.
- Implement application-specific browser scenarios.

## Decisions

1. `macwdo-tester` is a workflow skill, not a low-level CLI reference.

   It will specify the sequence: inspect context, validate linked worktree when applicable, load/use `portless`, launch through a routed `.localhost` URL, load/use `agent-browser`, verify with snapshot-driven interactions, then report. Command details remain in the source `portless` and `agent-browser` skills.

2. The existing `macwdo-agent-testing-*` guidance will be consolidated rather than expanded.

   The implementation should either remove the old granular testing skills or turn them into compatibility stubs that point to `macwdo-tester`. Router entries should prefer `macwdo-tester` so future discovery does not choose the old split workflow.

3. The tester agent config should expose one agent named `Macwdo Tester`.

   The default prompt should tell the agent to use `macwdo-tester`, `portless`, and `agent-browser`, inspect the current app/testing context, run the local verification workflow, stop on the first real blocker, and report the result.

4. The workflow should preserve strict local testing safeguards.

   The tester must not guess raw localhost URLs, continue clicking after a concrete failure, leave dev servers running unless asked, or skip the final report.

## Risks / Trade-offs

- Old prompts may still reference `macwdo-agent-testing-*` → Mitigation: leave compatibility stubs or clear redirects during migration.
- Consolidating leaves into one skill can make the skill too long → Mitigation: keep `macwdo-tester` workflow-focused and point to `agent-browser` and `portless` for detailed command references.
- Linked-worktree checks may not apply to every repository → Mitigation: require the tester to report when the current directory is not a linked worktree and only proceed differently when the user explicitly asks for a non-worktree verification.
- Browser automation can produce misleading results after a failed step → Mitigation: require snapshot, interact, wait, verify loops and stop at the first real blocker.

## Migration Plan

1. Add `.codex/skills/macwdo-tester/SKILL.md`.
2. Add `.codex/skills/macwdo-tester/agents/openai.yaml`.
3. Update `.codex/skills/macwdo/SKILL.md` and `.codex/skills/macwdo-explorer/SKILL.md` to route testing to `macwdo-tester`.
4. Replace old `macwdo-agent-testing-*` agent configs or skill bodies with compatibility redirects, or remove them if no compatibility is needed.
5. Validate Markdown, referenced paths, YAML, and OpenSpec status.

## Open Questions

- Should the old `macwdo-agent-testing-*` directories be removed entirely, or kept as compatibility stubs for one migration cycle?
