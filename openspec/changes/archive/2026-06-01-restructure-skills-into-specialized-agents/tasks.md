## 1. Inventory and Classification

- [x] 1.1 Inventory all active `.codex/skills/mires-*` directories and record their current role as public agent, router, granular leaf, workflow, or compatibility candidate.
- [x] 1.2 Define the public Mires agent-entrypoint allowlist and map every granular skill to an owning public agent or removal decision.
- [x] 1.3 Identify which existing `agents/openai.yaml` files can be reused and which new specialized agent configs are required.

## 2. Agent-First Skill Structure

- [x] 2.1 Update `.codex/skills/mires/SKILL.md` so it lists only public Mires agents and routing categories.
- [x] 2.2 Add missing specialized agent skills and `agents/openai.yaml` files for Django, FastAPI, LangGraph, React, and Next.js domains.
- [x] 2.3 Update existing planner, backend, tester, reviewer, researcher, and project-conventions agent prompts to load granular context only after domain selection.
- [x] 2.4 Move detailed granular implementation guidance into the owning agents' `references/` folders or another documented private support location.

## 3. Compatibility and Cleanup

- [x] 3.1 Replace retained granular `SKILL.md` files with concise compatibility redirect stubs that point to the owning specialized agent.
- [x] 3.2 Remove granular skill IDs from active namespace and explorer maps unless they are public agents or router entrypoints.
- [x] 3.3 Update active documentation to explain the agent-first structure, the public entrypoint list, and the migration path from direct granular invocations.
- [x] 3.4 Ensure archived OpenSpec history remains unchanged except for this new change directory.

## 4. Verification

- [x] 4.1 Add or update a verification command that reports public Mires agent entrypoints and fails when the namespace lists a broad granular skill catalog.
- [x] 4.2 Add or update verification that checks compatibility redirect stubs stay concise and do not duplicate former full implementation guides.
- [x] 4.3 Verify all moved `references/`, `agents/`, and relative links exist.
- [x] 4.4 Run `git status --short`, the documented verification command, and focused Markdown/YAML validation for touched files.

## 5. OpenSpec Completion

- [x] 5.1 Run `openspec status --change restructure-skills-into-specialized-agents` and confirm the change is apply-ready.
- [x] 5.2 After implementation, archive the change with `openspec archive restructure-skills-into-specialized-agents` once validation passes.
