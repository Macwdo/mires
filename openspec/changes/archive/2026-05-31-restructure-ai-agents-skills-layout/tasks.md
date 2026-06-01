## 1. Inventory and Layout Preparation

- [x] 1.1 Inventory current public Mires agents, compatibility redirect skills, agent metadata, and reference directories under `.codex/skills`.
- [x] 1.2 Create canonical `.ai/agents` and `.ai/skills` directories.
- [x] 1.3 Decide and document whether `.codex/skills` will be committed as a mirror or generated during package/build steps.
- [x] 1.4 Define the standard file shape for each `.ai/agents/<agent>/` directory, including where agent usage instructions and runtime metadata live.

## 2. Requested Agent Hierarchy

- [x] 2.1 Create `.ai/agents/mires-planner` with instructions describing how each agent in the hierarchy should be used.
- [x] 2.2 Create `.ai/agents/mires-explorer` with instructions for calling relevant subagents to explore repositories and identify bugs, errors, and risks.
- [x] 2.3 Create `.ai/agents/mires-tester`, `.ai/agents/mires-tester/mires-tester-agent-browser`, and `.ai/agents/mires-tester/mires-tester-portless` with tester delegation rules.
- [x] 2.4 Create `.ai/agents/mires-researcher` with MCP and WebSearch research instructions and citation/reference expectations.
- [x] 2.5 Create `.ai/agents/mires-backend/mires-python` and Python subagents for SQLAlchemy, AWS, TDD, patterns, class-based, and function-based work.
- [x] 2.6 Create `.ai/agents/mires-backend/mires-python/mires-python-fastapi` and FastAPI subagents for SQLAlchemy, Postgres, TDD, Celery, and Celery Beat.
- [x] 2.7 Create `.ai/agents/mires-backend/mires-python/mires-python-django` and Django subagents for models, serializer, APIs, apps, tests, Celery, Celery Beat, patterns, and TDD.
- [x] 2.8 Create `.ai/agents/mires-frontend/mires-react` and React subagents for React Query, React Hook Form, and Zod.
- [x] 2.9 Preserve Mires identifiers exactly as directory names and runtime metadata names.

## 3. Canonical Skill and Reference Migration

- [x] 3.1 Move reusable skill packages, compatibility redirect stubs, and support-skill instructions into `.ai/skills/<skill-name>/`.
- [x] 3.2 Move agent-owned reference material into the documented `.ai/skills` owner package locations.
- [x] 3.3 Preserve existing front matter names and owning-agent redirect targets during the move.

## 4. Codex Compatibility Export

- [x] 4.1 Create or update the export path that populates `.codex/skills` from canonical `.ai` assets.
- [x] 4.2 Ensure exported Codex skill packages preserve current discovery behavior and `agents/openai.yaml` compatibility where required.
- [x] 4.3 Prevent direct `.codex/skills` edits from becoming the source of truth by documenting and verifying the export relationship.

## 5. Documentation and Governance

- [x] 5.1 Update `AGENTS.md` to describe `.ai/agents` and `.ai/skills` as canonical and `.codex/skills` as compatibility output.
- [x] 5.2 Update `docs/mires-agent-architecture.md` with the new layout, ownership rules, public agent list, nested agent hierarchy, and reference locations.
- [x] 5.3 Update `.ai/skills/mires/SKILL.md` or its exported equivalent so namespace routing references the canonical layout.
- [x] 5.4 Update active OpenSpec docs or specs only where needed to remove stale `.codex/skills` source-of-truth wording.

## 6. Verification

- [x] 6.1 Update `scripts/verify_agent_first_surface.py` to validate the full requested `.ai/agents` hierarchy, agent instruction files, skill packages, references, and compatibility redirects.
- [x] 6.2 Add validation that `.codex/skills` is present and synchronized with the canonical `.ai` assets.
- [x] 6.3 Add path-reference validation for `.ai`, `.codex`, `docs`, and `scripts` paths in active Markdown files.
- [x] 6.4 Add validation that `mires-tester` references `mires-explorer`, tester subagents exist, and `mires-researcher` documents MCP or WebSearch usage.
- [x] 6.5 Run `python3 scripts/verify_agent_first_surface.py` and fix any reported drift or broken references.
- [x] 6.6 Run `git status --short` and confirm only intended restructure and OpenSpec files changed.
