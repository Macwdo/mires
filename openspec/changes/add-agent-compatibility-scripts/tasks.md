## 1. Repository Inspection

- [x] 1.1 Inspect existing `.ai/agents`, `.ai/skills`, runtime metadata, and verification script patterns before editing implementation files.
- [x] 1.2 Summarize Python/backend convention evidence for configuration, dependency injection, service boundaries, error handling, testing, naming, and module organization before implementation.

## 2. Python Package Structure

- [x] 2.1 Create `src/main.py` as the compatibility CLI entrypoint.
- [x] 2.2 Create the `src/compatibility/` package with modules for normalized models, parsing, and Codex compatibility.
- [x] 2.3 Keep runtime-specific behavior out of shared parsing and model modules.

## 3. Canonical Asset Parsing

- [x] 3.1 Implement discovery for canonical `.ai/agents/**/AGENT.md` and associated `agents/openai.yaml` metadata paths.
- [x] 3.2 Implement discovery for canonical `.ai/skills/**/SKILL.md` packages and declared reference paths.
- [x] 3.3 Parse required front matter and report missing or invalid fields with path-specific errors.
- [x] 3.4 Validate referenced files exist without treating archived OpenSpec history as active source.

## 4. Codex Compatibility Adapter

- [x] 4.1 Implement a Codex adapter that consumes normalized `.ai` models.
- [x] 4.2 Validate the Codex metadata fields currently used by bundled agents.
- [x] 4.3 Return a clear unsupported-target error for runtime targets other than Codex.
- [x] 4.4 Ensure the adapter does not create or require a second committed runtime authoring tree.

## 5. CLI and Documentation

- [x] 5.1 Add CLI behavior for running compatibility checks from the repository root.
- [x] 5.2 Document the compatibility command and the relationship between `.ai` source assets and runtime adapters.
- [x] 5.3 Update verification documentation if maintainers need a new command in addition to `python3 scripts/verify_agent_first_surface.py`.

## 6. Verification

- [x] 6.1 Add focused tests or script-level checks for parsing agents, parsing skills, Codex validation, and unsupported runtime handling.
- [x] 6.2 Update `scripts/verify_agent_first_surface.py` if needed so `src/compatibility/**` is accepted as tooling while duplicate runtime authoring trees still fail.
- [x] 6.3 Run `python3 scripts/verify_agent_first_surface.py`.
- [x] 6.4 Run the new compatibility workflow command and confirm it reports success for Codex.
- [x] 6.5 Run OpenSpec status for `add-agent-compatibility-scripts` and confirm the change remains apply-ready.
