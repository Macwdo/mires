## Context

Mires currently ships 99 Codex skill directories. The top-level `mires` skill lists many granular Python, Django, LangGraph, React, Next.js, testing, infrastructure, and DevEx skills, while only a small subset have `agents/openai.yaml` entrypoints. This makes the available skill surface broad enough that Codex sessions can spend context on skill metadata before the task domain is known.

The existing structure already has useful roles: namespace skills, explorer/router skills, workflow skills, leaf implementation skills, and agent-backed skills. The restructure should preserve those distinctions but change the default exposure model: users invoke specialized agents, and those agents load granular guidance only after their context is selected.

## Goals / Non-Goals

**Goals:**

- Reduce default Codex context consumed by Mires skill discovery.
- Make specialized agents the primary public entrypoints for work domains.
- Keep granular implementation guidance available inside the relevant agent context.
- Preserve compatibility for existing skill IDs through redirects or internal references.
- Make routing decisions explicit enough that future skills do not recreate the same broad context problem.

**Non-Goals:**

- Rewrite all implementation guidance content in this change.
- Add another runtime target beyond Codex.
- Remove the OpenSpec history or rewrite archived Macwdo-era changes.
- Build an automated semantic router or new external dependency.

## Decisions

### Public surface becomes agent-first

Expose a bounded public set of skills with agent configs:

- `mires`
- `mires-planner`
- `mires-project-conventions`
- `mires-backend-orchestrator`
- `mires-python-django-agent`
- `mires-python-fastapi-agent`
- `mires-python-langgraph-agent`
- `mires-typescript-react-agent`
- `mires-typescript-next-agent`
- `mires-tester`
- `mires-reviewer`
- `mires-backend-reviewer`
- `mires-researcher`

Rationale: this matches how users describe work while keeping task-specific context behind a small number of entrypoints.

Alternative considered: keep every granular skill public and improve descriptions. That preserves direct access but does not solve context pressure because every skill still competes in discovery.

### Granular skills become private support material or redirects

Move leaf guidance into one of two forms:

- `references/` files owned by a specialized agent skill when the content is only useful after that agent is selected.
- Compatibility `SKILL.md` redirect stubs when existing external prompts may still name the old skill ID.

Redirect stubs should be tiny: front matter plus one short instruction to use the owning agent. They must not carry the full implementation guide.

Rationale: this removes large leaf descriptions from default discovery while keeping old names discoverable enough to migrate.

Alternative considered: delete all granular skills immediately. That gives the smallest surface but makes existing prompts brittle and risks losing guidance before the new agents are proven.

### Routers list categories, not every leaf

The top-level `mires` namespace and explorer skills should describe the public agents and their domains. They should not enumerate every support reference or private leaf.

Rationale: the namespace should help select context, not become the context.

Alternative considered: retain a full skill map but mark entries as internal. That still expands the visible surface and invites direct invocation.

### Agent prompts own context loading

Each specialized `agents/openai.yaml` prompt should tell the agent which local references to inspect and when. For backend agents, the existing convention gate remains mandatory before implementation.

Rationale: prompts are the correct place to define domain-specific context loading, while `SKILL.md` remains a concise trigger and routing contract.

Alternative considered: put all agent workflow details in `SKILL.md`. That keeps everything in one file but recreates large skill payloads.

### Distribution verification enforces the new surface

Add or update verification to count public agent entrypoints, detect full leaf content in redirect stubs, and fail if the namespace reintroduces a broad leaf catalog.

Rationale: the main risk is regression through future skill additions. A cheap structural check is enough for this repository.

Alternative considered: rely on manual review only. That is workable short-term but does not protect the context budget over time.

## Risks / Trade-offs

- Existing direct skill invocations may become less precise -> Mitigate with compatibility redirect stubs and clear migration guidance.
- Specialized agents may become too large over time -> Mitigate by keeping `SKILL.md` concise and moving detailed domain docs into targeted `references/`.
- Some tasks span multiple domains -> Mitigate by routing through `mires-planner` or `mires-backend-orchestrator`, which can select a second agent only after convention discovery.
- Verification may overfit to current names -> Mitigate by using a maintained public-entrypoint allowlist and documenting how to add an agent.

## Migration Plan

1. Inventory all current `mires-*` skills and classify them as public agent, router, redirect, or private reference.
2. Create missing specialized agent skills and `agents/openai.yaml` files for Django, FastAPI, LangGraph, React, and Next.js.
3. Move detailed granular guidance into owning agents' `references/` folders.
4. Replace old granular `SKILL.md` files with small compatibility redirects or remove them from active distribution if no compatibility path is needed.
5. Update `mires` and explorer skills to list only public agents and routing categories.
6. Add verification for public surface size, redirect-stub shape, stale broad catalogs, and broken relative links.
7. Validate by invoking representative entrypoints and checking that each loads the right local references without exposing unrelated domains.
