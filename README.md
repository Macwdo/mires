# Mires

Mires is a Markdown-only repository of Macwdo's engineering skills, agents, and rules. Every file is Markdown.

The agents now run on OpenBot. The agent team, its routing, and its rules live in [`openbot/`](openbot/README.md). Skills still install into any runtime with the `skills` CLI.

## Install

Install with the [skills](https://github.com/vercel-labs/skills) CLI. List what is available:

```bash
npx skills add Macwdo/mires --list
```

Install every skill:

```bash
npx skills add Macwdo/mires --all
```

Install one skill, globally, for one agent:

```bash
npx skills add Macwdo/mires --skill mires-python-django -g -a codex
```

`bunx skills add ...` works the same way.

## Skills

| Skill | Owns |
| --- | --- |
| `mires` | Index of every Mires skill, plus the personal operating model, testing, and review |
| `mires-python` | Typed Python with uv, Ruff, ty, backend services, SQLAlchemy, Postgres, Celery, and tests |
| `mires-fastapi` | FastAPI app setup, routes, dependencies, schemas, session wiring, and Celery-backed endpoints |
| `mires-python-django` | Typed Django and DRF, with the full Django backend standard handbook in the same file |
| `mires-python-langchain` | Typed LangChain, LangGraph, Deep Agents, LLMs, loaders, retrieval, persistence, and tests |
| `mires-react` | React composition, state ownership, forms, accessibility, performance, and tests |
| `mires-next` | Next.js App Router, server/client boundaries, fetching, caching, mutations, security, and deployment |
| `mires-typescript` | Type ownership, shared contracts, runtime validation, and API integration |
| `convencoes-de-projeto` | Read a project's conventions before coding and verify with its own commands |
| `openbot-navegador-e-prints` | Open pages in the OpenBot browser and deliver screenshots as evidence |

## Layout

| Path | Contents |
| --- | --- |
| `skills/<slug>/SKILL.md` | The skill's complete guidance in one file. `skills/mires/SKILL.md` is the index. |
| `openbot/agents/<slug>.md` | OpenBot agent profiles: name, title, model, skills, and description. |
| `subagents/<slug>/AGENT.md` | Pre-OpenBot role prompts, kept as reference. |
| `rules/<slug>.md` | Standing rules that apply across work. |

## Adding A Skill

Create `skills/<slug>/SKILL.md` with YAML front matter (`name` equal to the slug, and `description`). Keep files Markdown only.
