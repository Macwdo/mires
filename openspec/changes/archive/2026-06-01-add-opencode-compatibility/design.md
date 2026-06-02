## Context

Mires stores canonical runtime assets under `.ai/agents` and `.ai/skills`. The current compatibility tooling parses those assets once, validates Codex-oriented runtime metadata, and can generate Codex install output under a Codex home directory. Documentation and verification currently assume Codex is the only supported runtime target and treat active OpenCode references as stale.

OpenCode supports Markdown agents in `~/.config/opencode/agents/` or `.opencode/agents/`, and discovers skills from `~/.config/opencode/skills/<name>/SKILL.md`, `.opencode/skills/<name>/SKILL.md`, and compatible `.agents` or `.claude` skill locations. Mires should generate OpenCode assets from the same `.ai` source, not commit a second OpenCode authoring tree.

## Goals / Non-Goals

**Goals:**
- Add `opencode` as a supported `src/main.py --target` value for `check` and `install`.
- Generate OpenCode Markdown agents and skill packages from canonical `.ai` assets.
- Keep generated OpenCode output out of the repository's active source tree.
- Preserve current Codex behavior and tests.
- Update documentation and repository verification to recognize OpenCode as an intentional supported target.

**Non-Goals:**
- Change the canonical `.ai` authoring layout.
- Add committed `.opencode` generated assets to the repository.
- Remove or redesign Codex support.
- Add provider/model-specific OpenCode configuration beyond the generated agents and skills needed for Mires behavior.

## Decisions

- Add a target dispatcher instead of extending the Codex adapter with OpenCode conditionals. This keeps target-specific rendering and install paths isolated while reusing the existing inventory parser and validation model.
- Create `src/compatibility/opencode.py` for OpenCode validation, rendering, and installation. This mirrors the current Codex module shape without sharing runtime-specific output code prematurely.
- Generate one Markdown agent per canonical Mires agent under `<opencode-home>/agents/<agent>.md`. The Markdown front matter should include the agent description and `mode`, and the body should point to the generated private bundle plus the agent's bundled skills.
- Generate private Mires skill packages under `<opencode-home>/skills/<skill>/SKILL.md` or agent-scoped bundles only if OpenCode discovery requires global skill visibility. Prefer global OpenCode skill packages for the canonical skill assets because OpenCode has native skill discovery and can load them on demand.
- Add an `--opencode-home` CLI option that defaults to `~/.config/opencode`, matching OpenCode's global configuration location.
- Keep verification strict about duplicate committed runtime assets while allowing active OpenCode adapter code, tests, and documentation.

## Risks / Trade-offs

- OpenCode agent Markdown schemas may evolve -> Keep generated fields minimal (`description`, `mode`, permissions only if needed) and validate generated front matter in tests.
- Global OpenCode skill installation can expose Mires skills to non-Mires agents -> Use Mires-namespaced skill IDs already present in canonical assets and document that install writes generated global OpenCode skills.
- Separate Codex and OpenCode adapters can duplicate bundle-copy helpers -> Accept small duplication initially or extract only obvious runtime-neutral helpers after both adapters are implemented.
- Verification currently flags OpenCode references as stale -> Update checks narrowly so they still reject committed `.opencode` runtime output while allowing intentional OpenCode support files.
