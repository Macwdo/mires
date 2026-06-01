## Why

Mires can validate Codex compatibility from canonical `.ai` assets, but it cannot install those agents into a user's Codex home. Maintainers need the script to materialize agents under `$HOME/.codex/agents/` and register them in `.codex/config.toml` so the canonical repository agents are usable by Codex without hand-copying files.

## What Changes

- Add an install operation to the compatibility script for the Codex target.
- Generate or refresh Codex agent files in `$HOME/.codex/agents/` from canonical `.ai/agents/<agent-name>/` sources.
- Update `$HOME/.codex/config.toml` by locating the existing `[agents]` section, or creating one when absent, and registering the installed agents.
- Preserve unrelated Codex configuration and make repeated installs idempotent.
- Keep `.ai/agents` as the only authoring source; installed files are derived runtime output, not a second committed authoring tree.
- Document validation and dry-run behavior for the install path.

## Capabilities

### New Capabilities
- `codex-agent-installation`: Installing canonical Mires agents into a user's Codex home and registering them in Codex configuration.

### Modified Capabilities
- `mires-agent-context-routing`: Clarify that canonical `.ai/agents` can be transformed into Codex-installed agents without becoming a committed second runtime authoring tree.

## Impact

- Affected paths: `src/main.py`, `src/compatibility/**`, `.ai/agents/**`, documentation that describes compatibility commands, and tests or verification scripts added for install behavior.
- Affected user files during install: `$HOME/.codex/agents/**` and `$HOME/.codex/config.toml`.
- No network access should be required.
- Config updates must preserve user-owned TOML content outside the managed agent registrations.
