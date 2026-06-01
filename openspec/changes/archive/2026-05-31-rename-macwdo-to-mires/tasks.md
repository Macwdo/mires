## 1. Package And CLI Rename

- [x] 1.1 Rename the CLI source files from `macwdo` to `mires` and update package `bin`, scripts, imports, help text, and command examples.
- [x] 1.2 Update package metadata and verification scripts from `@macwdo/macwdo` and Macwdo naming to `@mires/mires` and Mires naming.

## 2. Runtime Asset Rename

- [x] 2.1 Rename active `.codex/skills/macwdo*` directories to `.codex/skills/mires*` and update their front matter, headings, descriptions, and cross-skill references.
- [x] 2.2 Rename active `.opencode/skills/macwdo-*` and `.opencode/commands/macwdo-*` assets to `mires-*` and update their metadata and command text.
- [x] 2.3 Update bundled agent config display names, descriptions, and prompts to reference Mires and `$mires-*` skill IDs.

## 3. Documentation And Validation

- [x] 3.1 Update active README, architecture docs, install examples, and repository guidance to use Mires names while preserving archived OpenSpec history.
- [x] 3.2 Run syntax/package verification and fix any failures caused by renamed paths or executable names.
- [x] 3.3 Search active product files outside `openspec/changes/**` and remove any remaining `macwdo`, `Macwdo`, or `@macwdo` references.
