## Context

Mires currently treats `.ai/agents` and `.ai/skills` as the canonical runtime asset layout. That layout is intentionally agent-first and should remain the source authors edit, review, and verify.

The requested change adds Python compatibility scripts that can parse those canonical assets and adapt them for specific agent runtimes. Codex is the first supported target. OpenCode and other runtimes should be possible later, but the initial implementation should avoid designing around unverified target behavior beyond a narrow adapter boundary.

This repository does not currently have a Python package under `src/`, so the implementation should introduce the smallest package shape needed for maintainable parsing and CLI execution.

## Goals / Non-Goals

**Goals:**
- Add `src/main.py` as the initial Python entrypoint.
- Add `src/compatibility/` modules for parsing `.ai` agents and skills, normalized models, and runtime adapters.
- Make `.ai/agents` and `.ai/skills` runtime-agnostic canonical sources.
- Implement Codex compatibility first.
- Keep future runtime support behind an adapter interface.
- Add verification that exercises parsing and Codex compatibility behavior without requiring network or external services.

**Non-Goals:**
- Do not implement OpenCode compatibility in this change.
- Do not create a second committed runtime authoring tree.
- Do not replace the existing `.ai` agent-first routing model.
- Do not introduce broad packaging or publishing changes unless required to run the Python entrypoint.

## Decisions

### Use `.ai` as the canonical normalized source

The compatibility layer will read `.ai/agents/**/AGENT.md`, `.ai/agents/**/agents/openai.yaml`, and `.ai/skills/**/SKILL.md` as inputs. It will not ask maintainers to author runtime-specific duplicates.

Alternative considered: maintain separate Codex-ready files as source. That would conflict with the current agent-first `.ai` architecture and reintroduce duplicate runtime surfaces.

### Introduce a small `src/compatibility` package

Use a package shape similar to:

- `src/main.py`: CLI entrypoint and command dispatch.
- `src/compatibility/models.py`: normalized dataclasses for agents, skills, metadata, and validation messages.
- `src/compatibility/parsing.py`: filesystem discovery and front matter parsing for `.ai` assets.
- `src/compatibility/codex.py`: Codex adapter behavior.
- `src/compatibility/__init__.py`: package marker and public exports only when useful.

Alternative considered: place all logic in `src/main.py`. That would start simple but make future runtime adapters harder to isolate and test.

### Prefer standard-library parsing unless current files require more

Front matter parsing can begin with conservative standard-library string parsing because the repository uses simple YAML front matter. Runtime YAML metadata may need a YAML parser if existing metadata values exceed simple scalar/list handling. If a dependency is required, it should be added deliberately and covered by verification.

Alternative considered: add a YAML dependency immediately. That is acceptable if implementation discovers real metadata complexity, but it should not be assumed before inspecting the files.

### Treat Codex as an adapter, not the core model

Codex-specific output or validation rules belong in `src/compatibility/codex.py`. Shared parsing and normalized asset models stay runtime-neutral.

Alternative considered: make Codex the main model and add runtimes later by branching. That would make `.ai` less agnostic and increase the cost of adding OpenCode later.

## Risks / Trade-offs

- Runtime metadata semantics are underspecified -> Mitigate by validating only the Codex fields the repository already uses and documenting unsupported fields.
- Standard-library front matter parsing may miss complex YAML cases -> Mitigate with focused tests/fixtures and introduce a YAML dependency only if needed.
- Compatibility scripts could accidentally become a second runtime surface -> Mitigate by making generated/runtime-specific output derived and by extending verification to reject new active duplicate authoring trees.
- Future OpenCode behavior is unknown -> Mitigate by defining an adapter boundary without implementing speculative OpenCode rules.

## Migration Plan

1. Add the Python package structure under `src/`.
2. Implement parsing of canonical `.ai` agents and skills.
3. Implement Codex compatibility behavior using the normalized model.
4. Add or update verification commands so maintainers can run the workflow locally.
5. Update relevant documentation to describe `.ai` as runtime-agnostic source and Python scripts as compatibility tooling.

Rollback is straightforward: remove the new `src/` package and documentation/verification updates. Canonical `.ai` assets remain unchanged as the authoring source.

## Open Questions

- Should the first CLI command default to validation only, generation only, or both?
- Should Codex compatibility produce files on disk immediately, or only report what would be compatible until a later packaging change?
- Should runtime-specific outputs be ignored/generated artifacts or kept entirely outside the repository?
