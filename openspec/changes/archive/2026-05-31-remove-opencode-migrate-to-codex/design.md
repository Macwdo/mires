## Context

The current repository still contains an active split-runtime model: Codex assets under `.codex/skills/`, OpenCode assets under `.opencode/`, OpenCode-specific installer behavior in both `lib/mires-cli.js` and `install.sh`, and verification/docs that describe both runtimes. The requested direction is to stop shipping or documenting OpenCode entirely and make the active product surface Codex-only, while preserving archived OpenSpec history as historical record.

## Goals / Non-Goals

**Goals:**
- Remove active `.opencode` runtime assets and OpenCode-specific configuration from the repository product surface.
- Simplify the Node CLI and shell installer to a single Codex install model without runtime target selection.
- Rewrite active documentation, architecture guidance, and verification around Codex-only behavior.
- Preserve archived OpenSpec change history unchanged.

**Non-Goals:**
- Rewriting archived OpenSpec proposals, designs, or specs to erase historical OpenCode decisions.
- Introducing a new runtime abstraction or replacement for OpenCode commands.
- Preserving backward compatibility for `--target opencode` or `--target both`.

## Decisions

### Remove active OpenCode assets instead of keeping dormant copies

Delete the active `.opencode/` runtime tree and any product files that exist only for OpenCode, such as `opencode.json`. This keeps the repository aligned with the desired runtime model and removes the risk that packaging or docs accidentally expose stale OpenCode behavior later.

Alternative considered: keep `.opencode/` in-tree but stop documenting it. That would leave dead product surface area in place and keep maintenance/search noise high.

### Collapse installer logic to a single Codex payload model

Refactor the Node CLI and shell installer so they only plan, list, and install Codex skill directories. Remove runtime target selection, OpenCode destination resolution, OpenCode command copying, and any messaging that implies multi-runtime support.

Alternative considered: keep `--target codex` as a compatibility no-op. The request is to remove everything related to OpenCode, and a target flag implies a runtime matrix that no longer exists.

### Reframe verification around Codex-only expectations

Update package verification to assert that the tarball contains the Codex skill tree and excludes active OpenCode product assets. Validation should also search active repository files for stale `.opencode` and OpenCode references outside archived history, so future regressions are caught early.

Alternative considered: only remove `.opencode` files and leave existing verification mostly intact. That would make the tests lag behind the intended product contract.

### Keep archived OpenSpec history immutable

Do not rewrite files under `openspec/changes/archive/**` solely to remove OpenCode text. The active specs and source tree define the current contract; archives remain historical documentation of prior decisions.

Alternative considered: bulk-rewrite archives for consistency. That would damage change history and make prior design decisions harder to audit.

## Risks / Trade-offs

- Existing users may still rely on OpenCode install targets or command entrypoints -> Treat this as a breaking change in proposal, specs, and docs.
- Broad text replacement can accidentally modify archived history or unrelated strings -> Limit active-file edits intentionally and validate with targeted searches.
- Verification changes may miss a remaining OpenCode surface -> Add explicit failure checks for `.opencode`, `opencode.json`, and OpenCode wording in active product files.

## Migration Plan

1. Delete active `.opencode/` assets and remove any OpenCode-only config files from the product source tree.
2. Simplify `package.json`, `lib/mires-cli.js`, `install.sh`, and `scripts/verify-package.js` to a Codex-only package/install flow.
3. Rewrite active docs and architecture guidance to describe only Codex runtime behavior.
4. Update active OpenSpec requirements to define Codex-only distribution and validation expectations.
5. Validate with targeted searches and package verification, while leaving `openspec/changes/archive/**` untouched.

## Open Questions

- None.
