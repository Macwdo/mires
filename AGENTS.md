# Repository Guidelines

## Runtime Routing

Mires exposes two subagents. Route to them explicitly; the user should not have to name them.

- `explorer`: map files, entrypoints, dependencies, and existing patterns. Read-only. Use it when ownership is unclear or the relevant module is unknown.
- `planner`: turn an ambiguous request into a decision-ready plan. Use it when the task needs scoping before implementation.

Rules that apply to both:

- Inspect existing code patterns before proposing new ones.
- Prefer project conventions over generic advice.
- Separate discovered constraints from assumptions.
- Only one agent should modify files for a given change.

`planner` also serves as the reference shape for a new subagent: front matter, an `agents/openai.yaml`, a `## Skills` section listing the skills it loads, and a declaration in `state.yml`.

## Project Structure

`state.yml` is the catalog definition; `skills/`, `subagents/`, `rules/`, `mcps/`, and `hooks/` hold the files it declares. The `mires` CLI lives in `src/mires/`, with the state parser in `src/mires/state/`, runtime adapters in `src/mires/compatibility/`, repository scripts in `src/mires/scripts/`, and tests in `src/mires/tests/`.

Skills use `SKILL.md` with YAML front matter (`name`, `description`) and keep detailed material under `references/`. Subagents use `AGENT.md` with front matter (`name`, `description`, `parent`, `children`) plus `agents/openai.yaml`. Front matter `name` must equal the slug declared in `state.yml`.

Keep directory names lowercase kebab-case.

## Build, Test, and Development Commands

```bash
uv sync                                                   # install the toolchain
uv run mires validate                                     # catalog definition against the files on disk
uv run mires check --target codex                         # runtime compatibility
uv run python -m mires.scripts.verify_agent_first_surface # repository-wide surface checks
uv run pytest                                             # the test suite
```

Run all four before committing a change that touches the catalog or the CLI.

## Coding Style & Naming Conventions

Write documentation in clear, direct Markdown. Keep `AGENT.md` and `SKILL.md` action-oriented: when to use it, what workflow to follow, which references to load. Use two-space YAML indentation and keep examples small and specific.

Python is formatted and linted with Ruff at a 120-character line length (`uv run ruff check src`). Prefer explicit typing and small functions.

## AI Implementation Gate

Before backend implementation, inspect the target repository's conventions and summarize the evidence before editing code. This applies to work touching configuration, database access, dependency injection, services, repositories, error handling, testing, app startup, Celery, Django, FastAPI, or generic Python backend modules.

The convention report must cover the configuration pattern, database and session pattern, dependency injection style, service and repository boundaries, error handling style, testing style, and naming and module organization.

Existing project conventions override generic best practices and reusable skill examples. Do not introduce duplicate abstractions when the target repository already has a pattern. If a convention is unclear, report the uncertainty and choose the smallest reversible change instead of inventing architecture.

## Changing The Catalog

Adding, renaming, or removing a skill, subagent, rule, MCP server, or hook is a two-part change: the files and the `state.yml` entry. The validator rejects either half on its own, so keep them in the same commit and update every profile that should carry the entry.

Catalog membership is not hardcoded anywhere in Python. If a check needs to know what exists, it should read `state.yml` rather than grow its own list.

## Testing Guidelines

Tests live in `src/mires/tests/` and run under pytest. For documentation-only changes, validate by reading the rendered Markdown and confirming that referenced paths exist; `verify_agent_first_surface` checks inline backticked catalog paths automatically.

## Commit & Pull Request Guidelines

Use short imperative commit subjects, for example `add django endpoint skill` or `update python testing reference`. See `rules/commit-style.md`.

Pull requests should summarize which catalog entries changed, explain why, and list the manual validation performed.

## Security & Configuration

Do not commit secrets, personal tokens, API keys, or private environment values in any tracked file. Use placeholders such as `OPENAI_API_KEY`. See `rules/no-secrets.md`.
