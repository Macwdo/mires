## Why

The current Mires skill set is very granular and broad enough that Codex receives too much skill metadata in ordinary sessions. This change restructures Mires around fewer user-facing agent entrypoints, with granular guidance loaded only inside the specialized context that needs it.

## What Changes

- Introduce a small set of specialized Mires agent entrypoints for planning, backend work, Django, FastAPI, LangGraph, React/Next.js, testing, review, research, and project conventions.
- Move granular implementation guidance out of top-level skill discovery and into agent-owned references or private support skills.
- Keep the top-level `mires` namespace as a lightweight router instead of a complete catalog of every leaf skill.
- Update bundled agent prompts so each specialized agent loads only the context needed for its domain.
- Define compatibility behavior for existing granular skill IDs so old invocations redirect or remain internal without competing for context.
- **BREAKING**: Users and prompts should stop invoking most granular `mires-python-*` and `mires-typescript-*` skills directly; they should invoke specialized Mires agents instead.

## Capabilities

### New Capabilities

- `mires-agent-context-routing`: Defines how Mires exposes specialized agent entrypoints and keeps granular guidance out of default Codex context.

### Modified Capabilities

- `mires-namespace-distribution`: Updates packaged runtime assets and namespace expectations so the active distribution emphasizes agent entrypoints over a large public granular skill surface.

## Impact

- Affected files include `.codex/skills/mires*/SKILL.md`, `agents/openai.yaml` files, package/install verification if present, and OpenSpec documentation.
- No external runtime dependency is required, but the package contents and skill discovery surface will change.
- Implementation needs careful validation that old guidance is still reachable through agents while default sessions receive a much smaller active skill set.
