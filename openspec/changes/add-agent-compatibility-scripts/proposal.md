## Why

Mires currently documents `.ai/agents` and `.ai/skills` as canonical runtime assets, but compatibility with concrete agent runtimes is not managed by a first-class Python surface. A small compatibility layer is needed so the repository can keep authoring assets runtime-agnostic while generating or validating runtime-specific support, starting with Codex.

## What Changes

- Introduce a Python entrypoint at `src/main.py` for compatibility operations.
- Add a `src/compatibility/` package that owns parsing, normalized runtime models, and runtime adapters.
- Support Codex as the first concrete compatibility target.
- Keep `.ai/agents` and `.ai/skills` as the agnostic canonical source, with runtime adapters translating from that source instead of introducing another authoring tree.
- Preserve room for future OpenCode or other runtime adapters without implementing them in this change.
- Update verification/documentation paths so maintainers can understand and run the compatibility workflow.

## Capabilities

### New Capabilities
- `ai-runtime-compatibility`: Python-managed compatibility workflow that reads canonical `.ai` agents and skills and exposes runtime-specific support through adapters, starting with Codex.

### Modified Capabilities
- `mires-agent-context-routing`: Clarify that `.ai/agents` and `.ai/skills` are runtime-agnostic canonical sources and runtime-specific compatibility must be adapter-managed.
- `mires-namespace-distribution`: Clarify that active distribution may include Python compatibility scripts while still avoiding a second runtime authoring tree.

## Impact

- Affected paths: `src/main.py`, `src/compatibility/**`, `.ai/agents/**`, `.ai/skills/**`, `scripts/verify_agent_first_surface.py`, and related documentation.
- No external service dependencies are required.
- Python parsing should use standard-library APIs where practical, with any dependency additions justified explicitly.
- Future runtime targets such as OpenCode should be modeled as adapters but remain non-goals for the initial implementation.
