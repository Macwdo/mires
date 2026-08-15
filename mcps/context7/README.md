# Context7

Fetches current library, framework, and SDK documentation so agents do not answer from stale training data.

## Use When

An agent needs API syntax, configuration, migration steps, or CLI usage for an external library. Prefer it over a web search for library documentation.

## Configuration

`mcp.json` declares the server. `CONTEXT7_API_KEY` must be present in the environment; the value is never stored in this repository.
