# Mires

Mires is a Markdown-only repository of Macwdo's engineering skills, subagents, and rules. Every file is Markdown.

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

## Layout

| Path | Contents |
| --- | --- |
| `skills/<slug>/SKILL.md` | The skill's complete guidance in one file. `skills/mires/SKILL.md` is the index. |
| `subagents/<slug>/AGENT.md` | Subagent behavior. |
| `rules/<slug>.md` | Standing rules that apply across work. |

## Adding A Skill

Create `skills/<slug>/SKILL.md` with YAML front matter (`name` equal to the slug, and `description`). Keep files Markdown only.
