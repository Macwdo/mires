# Context7

Fetches current library, framework, and SDK documentation so agents do not answer from stale training data.

## Use When

An agent needs API syntax, configuration, migration steps, or CLI usage for an external library. Prefer it over a web search for library documentation.

## Configuration

`mcp.json` declares only the server command. In `state.yml`, top-level `secrets` declares `CONTEXT7_API_KEY` independently, while the `context7` entry under `mcps` references that secret and owns its target scope.

Set the variable before launching the target runtime. Mires renders only a runtime-native reference:

- Codex: `env_vars = ["CONTEXT7_API_KEY"]`
- Claude Code: `${CONTEXT7_API_KEY}`
- OpenCode: `{env:CONTEXT7_API_KEY}`

Cursor is intentionally outside this secret scope because its public MCP configuration documents literal `env` values but not a safe reference syntax. The value is never stored in this repository, generated runtime configuration, dry-run output, or install manifest.
