# No Secrets In Tracked Assets

Never commit secrets, personal tokens, API keys, or private environment values into skills, subagents, rules, MCP configuration, hooks, examples, or references.

## Rules

- Use placeholder names such as `OPENAI_API_KEY` or `DATABASE_URL` when configuration examples are necessary.
- Reference secrets through environment variables; never inline a literal value.
- Keep real credentials in the runtime environment or a secret manager, never in `state.yml` or any catalog entry.
- When an example needs a host, port, or account identifier, use an obviously fake value.

## On Discovery

If a secret is found in the repository, treat it as leaked: rotate the credential first, then remove it from the working tree. Removing the file alone does not undo the exposure.
