## 1. Inventory And Classification

- [x] 1.1 Inventory the existing Codex skill corpus before deletion and classify each Mires skill as routing domain, implementation reference, useful `.ai` redirect, or obsolete compatibility artifact.
- [x] 1.2 Compare the inventory with existing `.ai/agents/**/AGENT.md` entries and identify missing canonical agents or incomplete agent prompts.
- [x] 1.3 Define a maintained ownership mapping from migrated Mires skill domains to canonical `.ai/agents` owners and `.ai/skills` reference paths.

## 2. Canonical `.ai` Migration

- [x] 2.1 Add or update `.ai/agents` entries for migrated routing domains that are missing or incomplete in the canonical hierarchy.
- [x] 2.2 Ensure each migrated agent has `AGENT.md` front matter with `name`, `description`, `parent`, and `children`.
- [x] 2.3 Ensure each migrated agent has matching `agents/openai.yaml` runtime metadata using the same Mires identifier.
- [x] 2.4 Update parent agent delegation sections so backend, frontend, tester, explorer, researcher, review, project-convention, LangGraph, Next.js, and related migrated domains route to the most specific `.ai` agent.

## 3. References And Redirects

- [x] 3.1 Move or verify detailed guidance from retired granular skills into owner-specific `.ai/skills/**/references/` files.
- [x] 3.2 Convert useful legacy granular `.ai/skills/**/SKILL.md` files to concise redirects that name the canonical agent and reference owner.
- [x] 3.3 Remove obsolete compatibility-only skill packages that no longer need `.ai` redirects.
- [x] 3.4 Preserve OpenSpec utility skills only under canonical `.ai` or OpenSpec paths.

## 4. Remove Codex Surface

- [x] 4.1 Delete the active `.codex` runtime/export tree.
- [x] 4.2 Remove Codex export generation and sync-check behavior from active scripts.
- [x] 4.3 Remove active documentation and repository guidance that describes Codex as an install, runtime, discovery, export, or compatibility target.
- [x] 4.4 Ensure package or installer behavior references `.ai` assets only.

## 5. Documentation And Verification

- [x] 5.1 Update `.ai/skills/mires/SKILL.md` with the final `.ai` agent routing surface and `.ai` redirect policy.
- [x] 5.2 Update `docs/mires-agent-architecture.md` with the final hierarchy, reference ownership rules, and `.ai`-only runtime workflow.
- [x] 5.3 Extend `scripts/verify_agent_first_surface.py` to validate migrated skill ownership, agent metadata, reference existence, and absence of active `.codex` runtime assets.
- [x] 5.4 Run the updated agent-first verification command.
- [x] 5.5 Review `git status --short` and confirm only intended OpenSpec, `.ai`, docs, scripts, and removal changes are present.
