# Runtime-Agnostic Assets

Skills, rules, and agent prompts must work in any runtime (OpenBot, Claude Code, Devin, Codex, and others).

## Rules

- Describe capabilities, not tools: "open the page and take a screenshot", not one runtime's MCP tool name.
- When tool names help, put them in a per-runtime table inside the skill and keep the steps generic. The cross-runtime map lives in `RUNTIMES.md`; update it when a skill needs a new capability.
- Do not prefix a skill slug with a runtime name. Runtime-only files (`MIRES-OPENBOT.md`, `openbot/`) are the exception.
- When a capability is missing at runtime, the skill tells the agent to say so and continue, never to claim the check.
- Keep runtime-only keys (`runtime`, `provider`, `model`, `reasoning_effort`) in agent front matter; never in skill bodies.
