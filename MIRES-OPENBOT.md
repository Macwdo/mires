# Mires OpenBot

Bootstrap instructions for an OpenBot agent. When the owner says "read MIRES-OPENBOT.md" (or "set up Mires in OpenBot"), follow this file to make the local OpenBot match what Mires describes. Create only what is missing; never delete or overwrite anything without the owner's approval.

Source of truth in this repository:

- `openbot/README.md`: the team, routing, and rules.
- `openbot/agents/<slug>.md`: one agent profile per file. Front matter gives `display_name`, `title`, `provider`, `model`, `reasoning_effort`, and `skills`; the body's "Descrição" section is the profile description.
- `skills/<slug>/SKILL.md`: the skills that agents use.

## 1. Get The Repository

Use a local clone of `git@github.com:Macwdo/mires.git` (or `https://github.com/Macwdo/mires`). If one exists, `git pull --ff-only`; otherwise clone it into the owner's code folder. Read `openbot/README.md` and every file in `openbot/agents/`.

## 2. Compare With OpenBot

1. Call `openbot.list_agents`, then `openbot.read_agent` for each agent whose name matches a `display_name` in `openbot/agents/`.
2. For each Mires agent, classify it:
   - **missing**: no OpenBot agent has that name;
   - **different**: it exists, but title, description, model, effort, or skills differ;
   - **ok**: it matches.
3. Call `openbot.list_local_skills` and check that every skill named in any agent's `skills` exists in the local library.
4. Ignore OpenBot agents that are not in `openbot/agents/`. Never delete them.

## 3. Confirm The Plan

Show the owner one plan before changing anything: agents to create, agents to update with the exact differences, skills to create, and skills to install on each agent. Use an OpenBot confirm card. Do nothing the owner did not approve. If everything is **ok**, report that and stop.

## 4. Create Missing Skills

For each missing skill:

1. Copy `skills/<slug>/` into your own workspace.
2. Follow the `openbot-skill-creator` skill, then call `openbot.create_skill` with that folder as `sourcePath`.
3. Confirm with `openbot.list_local_skills` that it is in the library, and note its `skillId` and revision.

## 5. Create Or Update Agents

For a **missing** agent, call `openbot.create_agent`:

- `name`: `display_name`; `title`: `title`.
- `description`: the "Descrição" text plus the "Regra comum" line, at most 2000 characters.
- `provider`, `model`, `reasoningEffort`: call `openbot.list_models` first and pass them only if listed; otherwise omit them and say so.
- `initialMessage`: a short first task, for example "Read your profile and confirm your role in one line."

For a **different** agent, call `openbot.update_profile` with only the approved changes.

Then give each agent its skills with `openbot.install_local_skill` (its `agentId`, the `skillId`, and the latest revision). Check the result with `openbot.read_agent`.

## 6. Master Agent

The master agent (C'est Moi in `openbot/agents/c-est-moi.md`) keeps the rules from its "Instruções" section in its own instruction file (`AGENTS.md` in its workspace). If you are not the master agent, do not edit another agent's instructions or memory: report what the master agent must add, and the owner or the master applies it.

## 7. Project Channel (Optional)

If the owner wants a project channel, create it with `openbot.create_channel`, add the team, set C'est Moi as lead, and use the "Routing" list from `openbot/README.md` as the channel instructions.

## 8. Report

Report what was created, updated, skipped, and what failed, with the reason. Say which values could not be applied (for example a model that `openbot.list_models` does not list).

## Keeping Mires Current

When an agent changes in OpenBot (profile, model, or skills), update its file in `openbot/agents/`, and update `skills/` for changed skills. Commit and push with the owner's approval. Never commit employer-specific agents, paths, or data: this repository is public.
