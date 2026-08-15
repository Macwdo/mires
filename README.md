# Mires

Mires is Macwdo's personal engineering agent, versioned as one repository. It owns a catalog of skills, subagents, rules, MCP servers, and hooks, and installs a chosen slice of that catalog into a supported runtime.

`state.yml` is the definition. Every catalog entry is declared there and backed by real files in the matching directory. Nothing is discovered implicitly: an entry that is not declared is an error, and a declared entry without files is an error.

## Repository Layout

| Path | Contents |
| --- | --- |
| `state.yml` | The catalog definition and the profiles that select from it. |
| `skills/<slug>/SKILL.md` | Skill guidance, with detailed material under `references/`. |
| `subagents/<slug>/AGENT.md` | Subagent behavior, with runtime metadata in `agents/openai.yaml`. |
| `rules/<slug>.md` | Standing rules that apply across work. |
| `mcps/<slug>/mcp.json` | MCP server configuration. |
| `hooks/<slug>/hooks.json` | Hook definitions and their scripts. |
| `src/mires/` | The `mires` CLI: state parser, compatibility adapters, scripts, and tests. |
| `openspec/` | Spec-driven change proposals and their archive. |

## The State Definition

Each section is a list of entries with `name`, `slug`, and `description`. Skills also carry `visibility`, which decides how they are validated: `public` skills must ship `agents/openai.yaml` invoking `$<slug>`, and `private` skills must keep the six standard sections (`## When To Use`, `## Core Rules`, `## Preferred Patterns`, `## Anti-Patterns`, `## Checklist`, `## References Index`).

An entry lives at `<section>/<slug>` by default; set `path` to override it.

Profiles select slugs from those catalogs:

```yaml
config:
  profiles:
    - name: Tenant Evaluation
      slug: tenant-evaluation
      description: "Django backend work: the Django handbook plus the Python and data-layer skills."
      using:
        mcps: [context7]
        skills: [mires, mires-django, django, postgres, testing]
        subagents: [explorer, planner]
        rules: [no-secrets]
```

`using` also accepts a list of mappings, which the parser merges into one.

## Commands

Install the toolchain once with `uv sync`, then:

```bash
uv run mires validate                                    # check state.yml against the files on disk
uv run mires check --target codex                        # check runtime compatibility
uv run mires install --target codex                      # install the whole catalog
uv run mires install --target codex --profile personal   # install only what a profile selects
uv run mires install --target opencode --dry-run         # preview without writing
```

Validation runs before every check and install, so a broken catalog fails before anything is written.

Two more checks cover the repository as a whole:

```bash
uv run python -m mires.scripts.verify_agent_first_surface
uv run pytest
```

## Install Targets

`--target codex` writes generated agent config layers to `$HOME/.codex/agents/`, registers them in `$HOME/.codex/config.toml` under `[agents.<name>]`, and creates private agent bundles under `$HOME/.codex/mires/agents/<name>/`.

`--target opencode` writes generated Markdown agents to `$HOME/.config/opencode/agents/`, skills to `$HOME/.config/opencode/skills/`, and bundles to `$HOME/.config/opencode/mires/agents/<name>/`.

Everything under those homes is generated output. The canonical source is this repository; do not edit generated files. Use `--codex-home` or `--opencode-home` to install somewhere isolated.

## Public Skills

Three skills are marked `public` and are installable on their own:

```bash
bunx skills add Macwdo/mires --list
bunx skills add Macwdo/mires --skill mires -g -a codex
bunx skills add Macwdo/mires --skill mires-django -g -a codex
bunx skills add Macwdo/mires --skill mires-react -g -a codex
```

`mires-django` and `mires-react` carry full Markdown handbooks under `references/handbook/`, merged in from the former `django-cookiecutter-standard` and `react-personal-references` repositories. They are first-class content here now: edit the handbook Markdown directly.

## Adding A Catalog Entry

1. Create the files: `skills/<slug>/SKILL.md`, `subagents/<slug>/AGENT.md`, `rules/<slug>.md`, `mcps/<slug>/mcp.json`, or `hooks/<slug>/hooks.json`.
2. Declare the entry in `state.yml`, keeping the front matter `name` equal to the slug.
3. Add the slug to every profile that should use it.
4. Run `uv run mires validate`.

## Security

Do not commit secrets, personal tokens, API keys, or private environment values into any catalog entry, example, or reference. Use placeholders such as `OPENAI_API_KEY`. See `rules/no-secrets.md`.
