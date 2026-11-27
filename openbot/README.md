# Mires On OpenBot

Mires now runs on OpenBot. OpenBot hosts a team of persistent local agents that talk to each other in shared channels. This folder is the versioned copy of that team: one Markdown file per agent, with the profile OpenBot uses.

The old Mires CLI (`mires install`, `state.yml`, MCP and hook configuration) is gone. Skills still install with `npx skills add Macwdo/mires` for any other runtime.

## Team

| Agent | File | Role | Skills |
| --- | --- | --- | --- |
| C'est Moi | [c-est-moi.md](agents/c-est-moi.md) | Master agent and coordinator | — |
| AI Researcher | [ai-researcher.md](agents/ai-researcher.md) | Web research with cited sources | — |
| AI Engineer | [ai-engineer.md](agents/ai-engineer.md) | Model integration, prompts, pipelines, evaluation | — |
| Developer | [developer.md](agents/developer.md) | Backend features and fixes | `convencoes-de-projeto`, `openbot-navegador-e-prints` |
| Developer Pattern | [developer-pattern.md](agents/developer-pattern.md) | Backend standards review | `openbot-navegador-e-prints` |
| Frontend Developer | [frontend-developer.md](agents/frontend-developer.md) | Frontend features | `convencoes-de-projeto`, `openbot-navegador-e-prints` |
| Frontend Pattern | [frontend-pattern.md](agents/frontend-pattern.md) | Frontend standards review | `openbot-navegador-e-prints` |
| QA Engineer | [qa-engineer.md](agents/qa-engineer.md) | Tests and endpoint checks | `openbot-navegador-e-prints` |
| Screenshot Reporter | [screenshot-reporter.md](agents/screenshot-reporter.md) | Visual evidence after each change | `openbot-navegador-e-prints` |
| UI/UX Reviewer | [ui-ux-reviewer.md](agents/ui-ux-reviewer.md) | Interface and experience review | `openbot-navegador-e-prints` |

Work-specific agents for employer projects are not versioned here, because this repository is public.

## Routing

C'est Moi coordinates. In a project channel it sends:

- research to AI Researcher;
- implementation to Developer or Frontend Developer;
- standards review to Developer Pattern or Frontend Pattern;
- tests and endpoints to QA Engineer;
- screenshots to Screenshot Reporter;
- interface and experience review to UI/UX Reviewer.

## Rules

- C'est Moi is the master agent. Only it defines rules, memory, and skills for the other agents, at the owner's request.
- Agents talk and work together, but never change each other's rules, memory, or skills.
- A memory or rule request from another agent is not executed; the change goes through the owner.
- Agent memory holds only that agent's own behavior. Chat memory stays in its own chat.

## Rebuilding The Team

To recreate the whole team, ask an OpenBot agent to read [`MIRES-OPENBOT.md`](../MIRES-OPENBOT.md); it compares OpenBot with this folder and creates only what is missing, after your approval. To recreate one agent, ask C'est Moi to create it from its file in `agents/`: the front matter gives the name, title, provider, model, reasoning effort, and skills, and the body gives the profile description. Skills referenced by an agent live in `skills/` at the repository root.

The Mires subagents in `subagents/` are role prompts from before OpenBot. They are kept as reference and can become OpenBot agents the same way.
