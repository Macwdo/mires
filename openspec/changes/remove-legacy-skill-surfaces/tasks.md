## 1. Inventory And Ownership

- [x] 1.1 Search active repository files outside `openspec/changes/archive/**` for legacy granular skill IDs, compatibility redirects, duplicate runtime trees, and stale public skill references.
- [x] 1.2 Classify each legacy surface as obsolete, agent behavior, reusable reference guidance, or workflow-level guidance.
- [x] 1.3 Map each reusable legacy guide to the nearest owning `.ai/skills/<domain>` package or `.ai/agents/<agent>` workflow.

## 2. Reference Migration

- [x] 2.1 Move reusable legacy guidance into the owning `.ai/skills/<domain>/references/` path when no equivalent reference already exists.
- [x] 2.2 Update owner `SKILL.md` and relevant `AGENT.md` files to document when each retained reference may be loaded.
- [x] 2.3 Remove obsolete legacy content that is duplicated by existing agent instructions or existing references.

## 3. Legacy Surface Removal

- [x] 3.1 Delete active legacy granular skill packages and compatibility redirects whose guidance is now owner-loaded reference material.
- [x] 3.2 Update active prompts, runtime metadata, docs, and migration notes to route through owning agents or workflow packages instead of old granular skill IDs.
- [x] 3.3 Confirm archived OpenSpec history remains unchanged except for this new change directory.

## 4. Verification

- [x] 4.1 Extend `scripts/verify_agent_first_surface.py` to fail on active legacy granular skill packages, compatibility redirects, stale legacy skill IDs, and duplicate runtime assets.
- [x] 4.2 Extend verification so retained `.ai/skills/**/references/` files are documented by an owning `SKILL.md`, `AGENT.md`, or explicit allowlist.
- [x] 4.3 Run `python3 scripts/verify_agent_first_surface.py` and fix any failures.
- [x] 4.4 Run `git status --short` and review changed paths for unintended edits or deleted user work.
