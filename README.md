# Mires

Mires is Macwdo's personal engineering agent, versioned as one repository. It does two things: it holds the versioned state of every agent configuration, and it installs that state into whichever agent runtime is on the machine.

`state.yml` is the definition. Every catalog entry is declared there and backed by real files in the matching directory. Nothing is discovered implicitly: an entry that is not declared is an error, and a declared entry without files is an error.

## Install

One command provisions Codex, Cursor, Claude Code, and OpenCode with the whole catalog:

```bash
uvx --from git+https://github.com/Macwdo/mires mires install
```

No clone is needed. The catalog ships inside the package, so the command works from any directory. From a clone, `uv run mires install` does the same thing against the working tree.

Every install is idempotent, and re-running after dropping an entry from `state.yml` removes it from the runtimes too.

## Repository Layout

| Path | Contents |
| --- | --- |
| `state.yml` | The catalog definition and the profiles that select from it. |
| `skills/<slug>/SKILL.md` | Domain skill routing, with detailed material under `references/`. |
| `subagents/<slug>/AGENT.md` | Subagent behavior, with runtime metadata in `agents/openai.yaml`. |
| `rules/<slug>.md` | Standing rules that apply across work. |
| `mcps/<slug>/mcp.json` | MCP server configuration. |
| `hooks/<slug>/hooks.json` | Hook definitions and their scripts. |
| `src/mires/` | The `mires` CLI: state parser, runtime adapters, scripts, and tests. |

Adding a runtime means adding one adapter under `src/mires/compatibility/` and registering it in `targets.py`. The CLI has no per-runtime branches.

## The State Definition

Each section is a list of entries with `name`, `slug`, and `description`. Skills also carry `visibility`, which decides how they are validated: `public` skills must ship `agents/openai.yaml` invoking `$<slug>`, and `private` skills must keep the six standard sections (`## When To Use`, `## Core Rules`, `## Preferred Patterns`, `## Anti-Patterns`, `## Checklist`, `## References Index`).

An entry lives at `<section>/<slug>` by default; set `path` to override it.

Profiles select slugs from those catalogs:

```yaml
config:
  profiles:
    - name: Tenant Evaluation
      slug: tenant-evaluation
      description: "Django backend work: the core skill plus the Django and Python domains."
      using:
        mcps: [context7]
        skills: [mires, mires-python, mires-django]
        subagents: [explorer, planner]
        rules: [no-secrets]
```

`using` also accepts a list of mappings, which the parser merges into one.

## Commands

Install the toolchain once with `uv sync`, then:

```bash
uv run mires validate                                    # check state.yml against the files on disk
uv run mires check                                       # check every runtime for compatibility
uv run mires install                                     # install the whole catalog everywhere
uv run mires install --target cursor                     # install into one runtime
uv run mires install --profile personal                  # install only what a profile selects
uv run mires install --dry-run                           # preview without writing
```

`--target` accepts `codex`, `cursor`, `claude`, `opencode`, or `all`, and defaults to `all`. Validation runs before every check and install, so a broken catalog fails before anything is written.

Two more checks cover the repository as a whole:

```bash
uv run python -m mires.scripts.verify_agent_first_surface
uv run pytest
```

## What Lands Where

Every runtime receives the whole catalog, translated into that runtime's own conventions.

| Asset | Codex | Cursor | Claude Code | OpenCode |
| --- | --- | --- | --- | --- |
| Subagents | `agents/<slug>.toml` + `config.toml` | `agents/<slug>.md` | `agents/<slug>.md` | `agents/<slug>.md` |
| Skills | `skills/<slug>/` | `skills/<slug>/` | `skills/<slug>/` | `skills/<slug>/` |
| Rules | block in `AGENTS.md` | `plugins/local/mires/rules/<slug>.mdc` | block in `CLAUDE.md` | block in `AGENTS.md` |
| MCP servers | `config.toml` `[mcp_servers]` | `mcp.json` | `~/.claude.json` | `opencode.json` `mcp` |
| Hooks | not supported | `hooks.json` | `settings.json` | not supported |
| Specs | `mires/specs/` | `mires/specs/` | `mires/specs/` | `mires/specs/` |

Specs are optional: when an `openspec/specs/` directory exists at the catalog root, its Markdown is installed alongside everything else. There is none right now, so that row is inert.

Homes default to `~/.codex`, `~/.cursor`, `~/.claude`, and `~/.config/opencode`. Override any of them with `--codex-home`, `--cursor-home`, `--claude-home`, or `--opencode-home`.

Codex and OpenCode have no user-level hook runtime, so hooks are skipped there and the install says so.

Cursor is the one runtime with no global rules directory: its User Rules live in the settings store, and only project rules load from `.mdc` files. So Mires ships its rules as a local Cursor plugin. Cursor reloads `mcp.json` and `hooks.json` on save, but picks up a plugin on window reload, so run **Developer: Reload Window** after an install that changed rules.

### Hook Events

A hook binds to a canonical Mires event, and each runtime translates it. Cursor uses these names directly; Claude Code routes them through its own events and tool matchers.

| Mires event | Cursor | Claude Code |
| --- | --- | --- |
| `beforeSubmitPrompt` | `beforeSubmitPrompt` | `UserPromptSubmit` |
| `beforeShellExecution` | `beforeShellExecution` | `PreToolUse` matching `Bash` |
| `beforeReadFile` | `beforeReadFile` | `PreToolUse` matching `Read` |
| `afterFileEdit` | `afterFileEdit` | `PostToolUse` matching the edit tools |
| `stop` | `stop` | `Stop` |

Hook scripts are copied into the runtime home, so an install never depends on the repository staying where it is.

### Generated Output Is Not Yours To Edit

Everything Mires writes is generated from this repository. Mires shares those homes with you and with other tools, so it only ever touches what it owns: it replaces its own block in `AGENTS.md` and `CLAUDE.md`, and its own keys in `mcp.json`, `hooks.json`, `settings.json`, and `config.toml`. Your own servers, hooks, and prose survive an install.

What each install wrote is recorded in `<home>/mires/install-manifest.json`, which is how the next install knows what to remove.

## Skills

Skills are aggregated by domain, not by library. There is no per-library skill: a topic such as FastAPI, Celery, or Next.js is a rule document inside the domain that owns it.

| Skill | Domain | Topics |
| --- | --- | --- |
| `mires` | Personal and cross-cutting | Preferences, operating model, project conventions, testing, review, OpenSpec |
| `mires-python` | Python outside Django | Python, backend services, FastAPI, SQLAlchemy, Postgres, Celery, LangGraph |
| `mires-django` | Django and DRF | Django handbook, Django implementation rules |
| `mires-react` | React and Next.js | React and Next.js handbook, React, Next.js, frontend rules |
| `mires-typescript` | TypeScript | Type ownership, shared contracts, API integration |

Each `SKILL.md` routes by boundary. A topic lives at `references/<topic>/rules.md` with its focused reference documents beside it, so an agent loads only the rules for the boundary it is touching.

All five are marked `public` and are installable on their own:

```bash
bunx skills add Macwdo/mires --list
bunx skills add Macwdo/mires --skill mires -g -a codex
bunx skills add Macwdo/mires --skill mires-python -g -a codex
bunx skills add Macwdo/mires --skill mires-django -g -a codex
bunx skills add Macwdo/mires --skill mires-react -g -a codex
bunx skills add Macwdo/mires --skill mires-typescript -g -a codex
```

`mires-django` and `mires-react` carry full Markdown handbooks under `references/handbook/`, merged in from the former `django-cookiecutter-standard` and `react-personal-references` repositories. They are first-class content here now: edit the handbook Markdown directly.

## Adding A Catalog Entry

1. Create the files: `skills/<slug>/SKILL.md`, `subagents/<slug>/AGENT.md`, `rules/<slug>.md`, `mcps/<slug>/mcp.json`, or `hooks/<slug>/hooks.json`.
2. Declare the entry in `state.yml`, keeping the front matter `name` equal to the slug.
3. Add the slug to every profile that should use it.
4. Run `uv run mires validate`.

An MCP server is described once, in the shape `mcp.json` already uses (`command`, `args`, `env`, or `url`); each target reshapes it. A hook binds to a canonical event and keeps its scripts beside `hooks.json`.

## Adding A Topic

New guidance for a library or a practice is a topic, not a skill. Create `skills/<domain>/references/<topic>/rules.md` with the six standard sections (`## When To Use`, `## Core Rules`, `## Preferred Patterns`, `## Anti-Patterns`, `## Checklist`, `## References Index`), put its detailed documents beside it, and route to it from the domain's `SKILL.md`. Only add a new domain skill when the topic fits none of the existing five.

## Security

Do not commit secrets, personal tokens, API keys, or private environment values into any catalog entry, example, or reference. Use placeholders such as `OPENAI_API_KEY`. See `rules/no-secrets.md`.
