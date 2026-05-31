# Repository Guidelines

## Project Structure & Module Organization

This repository stores local Codex skills. Skill packages live under `.codex/skills/<skill-name>/`.
Each skill should include a `SKILL.md` with YAML front matter (`name`, `description`) followed by concise Markdown instructions. Use `references/` for supporting docs that are too detailed for the main skill, and `agents/` for agent configuration files such as `openai.yaml`.

Examples:

- `.codex/skills/macwdo/SKILL.md`: namespace entrypoint.
- `.codex/skills/macwdo-python-validation/SKILL.md`: focused reference material.
- `.codex/skills/macwdo-typescript-next-project-bootstrap/agents/openai.yaml`: agent configuration.

## Build, Test, and Development Commands

There is no application build or automated test suite configured in this repository. Useful local checks are:

- `rg --files .codex/skills`: list all tracked skill files.
- `sed -n '1,120p' .codex/skills/<skill>/SKILL.md`: review a skill quickly.
- `git status --short`: confirm only intended files changed.

When adding executable scripts or generated assets, document their commands in the related skill and update this guide if they become repository-wide.

## Coding Style & Naming Conventions

Write documentation in clear, direct Markdown. Keep `SKILL.md` files action-oriented: explain when to use the skill, what workflow to follow, and which references to load. Prefer lowercase kebab-case for skill directory names, matching existing patterns such as `macwdo-python-fastapi-patterns`.

Use YAML front matter consistently:

```yaml
---
name: skill-name
description: Short trigger-oriented description.
---
```

Use two-space indentation in YAML. Keep examples small and specific to the workflow.

## Testing Guidelines

For documentation-only changes, validate by reading the rendered Markdown and checking links to relative files. If a skill references `references/`, `agents/`, `scripts/`, or `assets/`, verify those paths exist. For YAML files, use a parser or editor validation before committing.

## Commit & Pull Request Guidelines

This repository has no existing commit history, so no local convention is established yet. Use short imperative commit messages, for example `add django endpoint skill` or `update python testing reference`.

Pull requests should summarize changed skills, explain why the change is needed, and list manual validation performed. Include screenshots only for changes that affect rendered documentation or visual assets.

## Security & Configuration Tips

Do not commit secrets, personal tokens, API keys, or private environment values in `SKILL.md`, `agents/*.yaml`, examples, or references. Use placeholders like `OPENAI_API_KEY` when configuration is necessary.
