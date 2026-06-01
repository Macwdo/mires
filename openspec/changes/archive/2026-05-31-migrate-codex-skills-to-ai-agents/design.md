## Context

Mires currently has canonical `.ai/agents` and `.ai/skills` assets, but the repository also carries `.codex/skills` as a compatibility export. The target state for this change is simpler: `.ai` is the only active runtime asset layout, and OpenSpec remains the change-management system.

The existing `.codex/skills` tree is useful only as migration input. Implementation should inspect it once to make sure no Mires domain behavior is lost, then remove the Codex surface and its sync workflow from active documentation and verification.

## Goals / Non-Goals

**Goals:**

- Inventory the existing Codex skill corpus before deletion and classify each Mires domain as an agent, agent-owned reference, or obsolete compatibility artifact.
- Ensure `.ai/agents` contains the canonical agent hierarchy needed to route every meaningful Mires implementation domain.
- Move prompt-level behavior, delegation, and runtime metadata into `AGENT.md` and `agents/openai.yaml`.
- Keep granular implementation instructions as `.ai/skills` references loaded by the owning agent only when needed.
- Remove `.codex/skills`, Codex export generation, Codex sync checks, and active docs that describe Codex as a runtime or install surface.
- Extend verification to enforce the `.ai`-only target state.

**Non-Goals:**

- Removing OpenSpec changes, specs, or `.ai/skills/openspec-*` skills.
- Reintroducing every granular skill as a public top-level agent.
- Rewriting archived OpenSpec history solely to remove historical references.

## Decisions

1. Treat `.codex/skills` as one-time migration input.

   Implementation may inspect existing Codex skill files to identify missing Mires behavior, but no new active behavior should be authored there. After migration, the `.codex` tree should be deleted and verification should fail if it returns.

   Alternative considered: keep `.codex/skills` as a generated export. That preserves duplicate runtime surface area, which is exactly what this change is meant to remove.

2. Use agent-owned coverage mapping instead of one agent per old skill.

   Domains such as Django, FastAPI, LangGraph, Next.js, React, testing, review, research, and project conventions should be represented by public or nested agents. Narrow implementation guides, such as serializer actions or test pagination, should remain references owned by the nearest agent.

   Alternative considered: generate an agent for every old skill ID. That would recreate the broad granular catalog in `.ai/agents` and make routing noisier.

3. Keep compatibility only inside `.ai` when it is still useful.

   Legacy skill IDs may remain as `.ai/skills` redirects if they help existing prompts transition, but they must point to canonical `.ai/agents` or `.ai/skills/**/references/` paths. There should be no Codex compatibility export.

   Alternative considered: delete every granular `.ai/skills` redirect immediately. That is cleaner, but it risks losing useful transition hints while the agent hierarchy settles.

4. Verify absence, not synchronization.

   Verification should check `.ai` agent coverage, reference existence, and the absence of `.codex` runtime assets. It should not run or require a Codex sync script.

   Alternative considered: keep sync checks as a guard. Sync checks are irrelevant once `.codex` is removed.

## Risks / Trade-offs

- Losing detailed guidance during deletion -> Inventory first and preserve useful content as `.ai/skills` references.
- Broadening `.ai/agents` too much -> Add nested agents only for meaningful routing domains and keep narrow guides as references.
- Breaking prompts that call old skill IDs -> Keep concise `.ai/skills` redirects where useful, but do not export them to Codex.
- Stale documentation -> Update the namespace skill, architecture docs, and repository guidance in the same implementation.
- Tooling assumptions about `.codex/skills` -> Remove or update scripts and verification so failures point to `.ai` assets.

## Migration Plan

1. Inventory the existing Codex skill corpus and record which content must be preserved in `.ai`.
2. Add or update missing `.ai/agents` entries and runtime metadata for meaningful routing domains.
3. Move or confirm detailed guidance under owner-specific `.ai/skills/**/references/`.
4. Convert useful legacy granular `.ai/skills/**/SKILL.md` files to concise redirects.
5. Remove `.codex/skills` and Codex export/sync tooling from active repository behavior.
6. Update `docs/mires-agent-architecture.md`, `.ai/skills/mires/SKILL.md`, repository guidance, and verification scripts for `.ai`-only runtime assets.
7. Validate with the updated agent-first verification command and `git status --short`.
