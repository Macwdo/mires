## Why

The repository is already moving to an agent-first `.ai` runtime, but legacy skill compatibility and broad skill catalogs can still compete with subagent routing. This cleanup makes the active surface stricter: useful legacy skill content is preserved only as owner-loaded reference material, and obsolete skill packages disappear from public discovery.

## What Changes

- **BREAKING** Remove active legacy granular skill packages and compatibility redirects when their content can be owned by an existing specialized agent or workflow package.
- Move any still-useful legacy skill instructions into the closest agent-owned `.ai/skills/<domain>/references/` file before deleting the legacy skill package.
- Update agent and skill documentation so public routing points to `.ai/agents/**` first, with `.ai/skills/**/references/` used only as selected context.
- Tighten verification so active files fail on stale legacy skill IDs, duplicate skill packages, and reference files without a documented owning agent or workflow.
- Preserve archived OpenSpec history as historical record; do not rewrite archive files solely to remove old names.

## Capabilities

### New Capabilities

### Modified Capabilities

- `mires-agent-context-routing`: Require granular legacy guidance to be either moved under an owning agent/workflow reference path or removed, with no public compatibility skill retained when an agent-owned reference is sufficient.
- `mires-namespace-distribution`: Require active distribution and verification to exclude legacy skill surfaces and to document the agent or workflow package that owns each retained reference.

## Impact

- Affects `.ai/agents/**/AGENT.md`, `.ai/skills/**/SKILL.md`, `.ai/skills/**/references/**`, active repository docs, and `scripts/verify_agent_first_surface.py`.
- Removes or forbids active legacy skill directories and compatibility redirects outside archived OpenSpec history.
- May break prompts that invoke old granular skill IDs directly; those prompts must route through the owning Mires agent or workflow instead.
