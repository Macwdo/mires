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
| `skills/<slug>/SKILL.md` | The skill's complete, self-contained guidance. |
| `subagents/<slug>/AGENT.md` | Subagent behavior, with runtime metadata in `agents/openai.yaml`. |
| `rules/<slug>.md` | Standing rules that apply across work. |
| `mcps/<slug>/mcp.json` | MCP server configuration. |
| `hooks/<slug>/hooks.json` | Hook definitions and their scripts. |
| `src/mires/` | The `mires` CLI: state parser, project sync, runtime adapters, scripts, and tests. |

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
        skills: [mires, mires-python, mires-python-django]
        subagents:
          - mires-technical-context-explorer
          - mires-technical-standards-reviewer
          - mires-business-context-explorer
          - mires-business-rules-reviewer
          - planner
        rules: [no-secrets]
```

`using` also accepts a list of mappings, which the parser merges into one.

Specialized explorer and reviewer slugs use `mires-<domain>-<focus>-<role>`, with full domain names such as
`technical` and `business`. Keep `explorer` and `reviewer` as the final role segment so routing remains predictable.

Secrets are independent declarations, never stored values. A secret knows only its identity and environment source.
Consumers reference it from their own catalog entry:

```yaml
secrets:
  - name: Context7 API Key
    slug: context7-api-key
    description: "Environment-backed credential for authenticated Context7 access."
    source:
      env: CONTEXT7_API_KEY

mcps:
  - name: Context7
    slug: context7
    description: "Current library documentation."
    secrets:
      - secret: context7-api-key
        env: CONTEXT7_API_KEY
        targets: [codex, claude, opencode]
```

The dependency is unidirectional: the MCP references the secret; the secret never names or scopes itself to an MCP.
Profiles do not repeat secret slugs. Selecting an MCP follows its references and selects only the secrets it consumes.
The schema deliberately rejects literal secret values. Each adapter renders a runtime-native environment reference;
it never reads, logs, copies, or records the credential in the install manifest.

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

Project configuration is a separate command group. See [Projects](#projects). `mires project-sync` is short for `mires project sync`.

Two more checks cover the repository as a whole:

```bash
uv run python -m mires.scripts.verify_agent_first_surface
uv run ruff format --check src
uv run ruff check src
uv run ty check
uv run pytest
```

Python tooling is standardized on uv, Ruff, and `ty`. uv owns the environment and lockfile, Ruff owns formatting and linting, and `ty` owns static type checking.

## Projects

A project is any directory with `.mires/state.yml`. That file is the only list of what syncs: catalog entries the project keeps under `.mires/`, plus `project.include` for paths the tools already use, often ignored by the project's own git repository. Source code never travels. The machine-wide catalog and `mires install` are unchanged.

The sync repository is ordinary git. Mires keeps a clone under `~/.mires/sync/` and reads and writes `projects/<slug>/`, mirroring project-relative paths exactly. Private or public is the repository's own setting; any URL works.

```yaml
version: 1

project:
  name: Project X
  slug: project-x
  remote:
    repo: git@github.com:you/your-repo.git   # or MIRES_SYNC_REPO, or ~/.mires/config.yml
    branch: main
    prefix: projects
  include:
    - .cursor/skills/internal-billing
    - .claude/agents/reviewer.md
    - AGENTS.md

skills:
  - name: Internal Billing
    slug: internal-billing
    description: "Rules this project keeps out of its own repository."
```

`include` must be a path inside the project. Absolute paths, `..`, `.git`, and `.mires` are rejected.

```bash
uv run mires project init [--slug x] [--repo URL]   # create .mires/state.yml here
uv run mires project list                           # projects already in the sync repository
uv run mires project status                         # local vs the repository
uv run mires project sync  [--slug x] [--pull|--push] [--dry-run]
uv run mires project pull  [--slug x] [--dry-run]
uv run mires project push  [--slug x] [--dry-run] [-m MSG]
uv run mires project-sync  ...                      # same as `mires project sync`
```

`sync` copies toward the side that is missing. When both sides exist, it copies the side that moved since the last sync. If both moved, it stops and asks for `--pull` or `--push`. `--pull` and `--push` overwrite that side completely for the declared payload.

A first `mires project-sync --slug project-x` in an empty directory clones the sync repository and writes the payload here. Push refuses files that look like credentials (`.env`, `*.pem`, `id_rsa*`, `credentials.json`) unless you pass `--allow-secrets`. Git that is not a fast-forward fails with the path of the clone so you can resolve it there.

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

Each catalog skill is a real, independently installable package. Its complete guidance lives in `SKILL.md`; related skills reference each other by `$slug`.

Every public skill is snippet-driven. Before generating implementation code, the agent selects the closest relevant snippet, compares it with the target repository, and adapts its ownership, typing, dependency, error, and test shape to local conventions. Snippets are mandatory reference implementations, not copy-paste templates.

| Skill | Owns |
| --- | --- |
| `mires` | Personal operating model, repository discovery, testing, review, and companion routing |
| `mires-python` | Typed Python with uv, Ruff, ty, backend services, FastAPI, SQLAlchemy, Postgres, Celery, and tests |
| `mires-python-django` | Typed Django and DRF models, services, APIs, security, tests, and operations |
| `mires-python-langchain` | Typed LangChain, LangGraph, Deep Agents, LLMs, loaders, retrieval, persistence, and tests |
| `mires-react` | React composition, state ownership, forms, accessibility, performance, and tests |
| `mires-next` | Next.js App Router, server/client boundaries, fetching, caching, mutations, security, and deployment |
| `mires-typescript` | Type ownership, shared contracts, runtime validation, and API integration |

All seven are marked `public` and are installable on their own:

```bash
bunx skills add Macwdo/mires --list
bunx skills add Macwdo/mires --skill mires -g -a codex
bunx skills add Macwdo/mires --skill mires-python -g -a codex
bunx skills add Macwdo/mires --skill mires-python-django -g -a codex
bunx skills add Macwdo/mires --skill mires-python-langchain -g -a codex
bunx skills add Macwdo/mires --skill mires-react -g -a codex
bunx skills add Macwdo/mires --skill mires-next -g -a codex
bunx skills add Macwdo/mires --skill mires-typescript -g -a codex
```

`agents/openai.yaml` remains beside each public skill because the runtimes use it for display metadata and invocation prompts. It is not a second instruction document.

## Adding A Catalog Entry

1. Create the files: `skills/<slug>/SKILL.md`, `subagents/<slug>/AGENT.md`, `rules/<slug>.md`, `mcps/<slug>/mcp.json`, or `hooks/<slug>/hooks.json`.
2. Declare the entry in `state.yml`, keeping the front matter `name` equal to the slug.
3. Add the slug to every profile that should use it.
4. Run `uv run mires validate`.

An MCP server is described once, in the shape `mcp.json` already uses (`command`, `args`, `env`, or `url`); each target reshapes it. Define environment-backed credentials in top-level `secrets`, then reference them from the consuming MCP entry in `mcps`. Never put literal credentials in either section or in `mcp.json`. A hook binds to a canonical event and keeps its scripts beside `hooks.json`.

## Adding A Skill

Create `skills/<slug>/SKILL.md` with all actionable guidance, a `## Snippet-Driven Implementation` section, and concrete implementation snippets. Add `agents/openai.yaml` for public runtime metadata, declare the slug in `state.yml`, and add it to each profile that should install it. Reference companion skills by `$slug`; do not create nested instruction trees.

## Security

Do not commit secrets, personal tokens, API keys, or private environment values into any catalog entry, example, or reference. Top-level `secrets` accepts environment variable names only; consumers own their references and target scopes. Neither form accepts values. See `rules/no-secrets.md`.
