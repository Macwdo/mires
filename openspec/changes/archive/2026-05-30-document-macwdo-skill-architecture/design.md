## Context

This repository packages local agent skills and runtime entrypoints rather than application code. The main source tree is `.codex/skills/`, where Macwdo guidance is expressed as Markdown skill packages. The OpenCode runtime has parallel installable assets under `.opencode/skills/` and `.opencode/commands/`, while `openspec/changes/` tracks proposed changes through proposal, design, specs, and tasks artifacts.

The current Macwdo skill hierarchy is intentionally granular. `.codex/skills/macwdo/SKILL.md` is the principal namespace and skill map. Explorer skills such as `macwdo-explorer`, `macwdo-python-django-explorer`, `macwdo-python-langgraph-explorer`, and `macwdo-typescript-next-explorer` route broad requests to narrower leaves. Leaf skills then encode specific implementation rules such as Django service functions, React server state, LangGraph graph assembly, or FastAPI route patterns.

This structure is mostly sound, but it is hard to evaluate because the architecture is distributed across many `SKILL.md` files. The implementation should make the model explicit without reorganizing working skills or changing installer behavior.

## Goals / Non-Goals

**Goals:**

- Explain the repository layout for Codex skills, OpenCode skills, OpenCode commands, agent configs, and OpenSpec changes.
- Describe the intended role of namespace skills, explorer/router skills, leaf skills, workflow skills, and `agents/openai.yaml` files.
- Give a practical evaluation framework for deciding whether the current structure is good and how new guidance should be added.
- Call out current strengths, risks, and recommended maintenance practices.
- Keep the guide direct enough to help both the repository owner and future agents understand the system quickly.

**Non-Goals:**

- Rename, merge, split, or delete existing skills.
- Add new installer behavior, package metadata, commands, or runtime paths.
- Convert Codex-only leaf skills into OpenCode skill packages.
- Replace OpenSpec, Codex, or OpenCode conventions with a new custom schema.
- Turn every implementation preference into a capability spec.

## Decisions

### Add a dedicated architecture guide under documentation

Create a focused Markdown document that explains the skill architecture from the repository root rather than burying the explanation in one skill file.

Alternative considered: expand `.codex/skills/macwdo/SKILL.md` with the full explanation. That file should stay a compact runtime routing entrypoint; a longer architecture guide would make agents load more prose than needed before selecting a leaf skill.

### Preserve the router and leaf skill model

Treat the current model as the recommended baseline: broad namespace and explorer skills should route, while leaf skills should contain concrete rules and examples.

Alternative considered: collapse many small leaves into fewer large family guides. That would reduce file count but make skill loading less precise and increase the chance of unrelated guidance polluting implementation decisions.

### Document evaluation criteria instead of enforcing a generator

Add human-readable criteria for when to create a router, leaf, command, or agent-backed workflow.

Alternative considered: add a script that validates skill shape. That may be useful later, but the immediate problem is conceptual clarity, not mechanical validation.

### Keep recommendations actionable and repo-specific

The guide should include direct judgments about the current structure: what is working, what could drift, and what should be improved next.

Alternative considered: write generic agent-skill best practices. Generic advice would not answer the user's question about whether this repository's specific Markdown structure is the best way to encode implementation preferences.

## Risks / Trade-offs

- Documentation can drift from the actual skill tree -> Keep the guide linked to stable concepts and update it when adding or removing major skill families.
- A guide may duplicate some information from `macwdo` and `macwdo-explorer` -> Keep those files as runtime maps and keep the new guide focused on architecture and evaluation.
- Recommendations could imply a larger refactor than intended -> Mark structural changes as future options unless required for the current documentation goal.
- The guide will not enforce consistency by itself -> Treat validation scripts as a possible future enhancement after the desired structure is clear.

## Migration Plan

1. Add the architecture guide as documentation-only content.
2. Add the capability spec that defines what the guide must explain.
3. Update task tracking for implementation and validation.
4. Validate by checking the referenced files exist and reading the guide for accuracy against the current tree.

Rollback is deleting the added documentation and OpenSpec change artifacts. No runtime state or package installation behavior changes.

## Open Questions

- Should the architecture guide live in `docs/` or be referenced from `README.md` after implementation? Default: add `docs/macwdo-skill-architecture.md` and link it from `README.md` so users can discover it.
