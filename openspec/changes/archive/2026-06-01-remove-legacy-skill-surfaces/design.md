## Context

Mires now uses `.ai/agents` as the public routing surface and `.ai/skills` as compact domain packages with detailed reference material. The current state still includes legacy concepts in active requirements and migration paths: standalone granular skill IDs, compatibility redirects, and broad skill catalogs that can compete with specialized subagent routing.

This change narrows the active model. A legacy skill is either useful implementation guidance, in which case it belongs under the closest owner package as reference material, or it is obsolete, in which case it is removed from active source. Archived OpenSpec changes remain historical and are not part of the cleanup target.

## Goals / Non-Goals

**Goals:**

- Remove active legacy skill packages, redirects, and docs when a specialized agent or workflow can own the behavior.
- Preserve reusable implementation guidance by moving it under `.ai/skills/<owner>/references/`.
- Make ownership explicit enough that verification can fail on orphaned references and stale skill IDs.
- Keep public discovery centered on `.ai/agents/**`.

**Non-Goals:**

- Do not rewrite archived OpenSpec history for terminology cleanup.
- Do not add a second export tree or compatibility distribution.
- Do not redesign the existing specialized agent hierarchy unless a missing owner is discovered.

## Decisions

### Inventory before deletion

Implementation should first inventory active skill-like assets and classify each item as agent behavior, reusable reference guidance, or obsolete content. This avoids losing useful project conventions while still removing public legacy surfaces.

Alternative considered: delete all legacy skill files immediately. That is faster but risks discarding detailed guidance that specialist agents still need.

### References live under owner skill packages

Reusable content should move to the closest existing owner under `.ai/skills/<domain>/references/`, such as backend, django, testing, openspec, react, next, or review. Agent prompts and `SKILL.md` files should mention only the references they may load, not expose those references as public routing targets.

Alternative considered: put all migrated references under a single `legacy/` package. That would preserve files but keep legacy organization as active architecture.

### Remove compatibility redirects by default

Legacy granular skill IDs should not remain as active redirect packages when an agent-owned reference exists. Compatibility redirects keep old names discoverable and weaken the agent-first contract. If a prompt still names an old skill ID, the active docs should point to the owning agent or workflow instead.

Alternative considered: retain redirects indefinitely. That reduces short-term prompt breakage but preserves duplicate public behavior and makes routing ambiguous.

### Verification enforces ownership and absence

`scripts/verify_agent_first_surface.py` should assert that active files do not reintroduce duplicate runtime trees, legacy granular skill packages, or stale public skill IDs. It should also validate that retained reference files are reachable from an owning `.ai/skills/<domain>/SKILL.md`, `.ai/agents/<agent>/AGENT.md`, or documented verification allowlist.

Alternative considered: rely on manual review. Manual checks are not durable enough for a repository whose main product is routing metadata.

## Risks / Trade-offs

- Old prompts that invoke granular skill IDs directly break → Document the owning agent/workflow route and update active prompts/configs in the same implementation.
- Useful guidance may be deleted accidentally → Require an inventory step and preserve reusable content as references before removal.
- Verification may be too strict for future additions → Keep the expected public surface explicit and require intentional updates when new agents or reference owners are added.
- Reference ownership can become noisy → Prefer domain-level owner packages over one-off compatibility packages.

## Migration Plan

1. Inventory active skill and reference surfaces outside `openspec/changes/archive/**`.
2. For each legacy skill-like item, classify it as obsolete, agent behavior, or reusable reference guidance.
3. Move reusable guidance into the nearest `.ai/skills/<owner>/references/` path and update the owner `SKILL.md` or agent `AGENT.md` to reference it.
4. Delete active legacy packages and compatibility redirects that are now represented by agent-owned references.
5. Update active documentation and runtime metadata to use the owning agents/workflows.
6. Extend and run `python3 scripts/verify_agent_first_surface.py`.

Rollback is a normal git revert of the cleanup change. If a specific deleted guide is needed later, restore it as an owner reference, not as a public legacy skill.

## Open Questions

- Whether any currently retained `.ai/skills/*/SKILL.md` packages are still too public and should become pure references owned directly by `.ai/agents`.
- Whether verification should allow a small explicit list of workflow skills, such as OpenSpec, that remain public because they are invoked directly.
