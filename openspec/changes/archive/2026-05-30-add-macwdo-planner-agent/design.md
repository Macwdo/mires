## Context

This repository stores local Codex skills under `.codex/skills/<skill-name>/`. Most skills already include compact `agents/openai.yaml` configs, and `macwdo-reviewer` already exists as a review router skill. The missing piece is a planning router that chooses relevant Macwdo leaf skills before implementation and turns their guidance into a concrete plan.

The implementation is documentation/config only: no application runtime, dependency, or data model changes.

## Goals / Non-Goals

**Goals:**

- Add `macwdo-planner` as a discoverable local skill and OpenAI agent config.
- Make planner behavior explicit: inspect the request/repo, choose relevant Macwdo skills, load their guidance, and produce a decision-complete plan.
- Keep reviewer behavior findings-first and tied to current code, git diff, and relevant Macwdo patterns.
- Register the planner in the Macwdo namespace and explorer maps.

**Non-Goals:**

- Do not change the semantics of Macwdo leaf implementation skills.
- Do not add scripts, runtime code, or external dependencies.
- Do not replace the existing `macwdo-reviewer` skill.

## Decisions

- Add a new `macwdo-planner` skill instead of expanding `macwdo-explorer`.
  - Rationale: explorer remains a skill-selection map, while planner owns the workflow for turning selected skill guidance into a full implementation plan.
  - Alternative considered: make `macwdo-explorer` produce plans. That would mix routing and planning responsibilities.
- Keep `macwdo-reviewer` as the only review skill and update only its agent prompt.
  - Rationale: the current reviewer skill already describes the right review workflow; the agent entry prompt just needs to make the expected repo and diff inspection explicit.
  - Alternative considered: create a second reviewer agent package. That would duplicate an existing skill and make discovery ambiguous.
- Register `macwdo-planner` in both `macwdo` and `macwdo-explorer`.
  - Rationale: `macwdo` is the namespace entrypoint, while `macwdo-explorer` is the detailed router used by agents and subagents.

## Risks / Trade-offs

- Planner might load too many skills for broad requests -> Mitigation: instruct it to use the narrowest matching leaf skills and avoid unrelated leaves.
- Planner could drift into implementation -> Mitigation: explicitly state it must plan and not edit code unless a later implementation request is made.
- Reviewer prompt could become too long for the agent menu -> Mitigation: keep YAML prompt concise and leave full workflow details in `SKILL.md`.
