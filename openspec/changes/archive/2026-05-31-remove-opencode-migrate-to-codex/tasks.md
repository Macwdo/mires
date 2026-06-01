## 1. Remove Active OpenCode Assets

- [x] 1.1 Delete the active `.opencode/` runtime asset tree and remove `opencode.json` from the product source.
- [x] 1.2 Remove any remaining active-file imports, paths, or assumptions that depend on `.opencode` assets existing.

## 2. Simplify Package And Installer Logic

- [x] 2.1 Update `package.json` publish metadata to bundle only Codex assets and Codex-oriented package descriptions.
- [x] 2.2 Refactor `lib/mires-cli.js` to remove OpenCode targets, OpenCode asset listing, and OpenCode destination planning.
- [x] 2.3 Refactor `install.sh` to remove OpenCode install paths, prompts, and copy routines so it installs only Codex assets.

## 3. Rewrite Documentation And Active Specs

- [x] 3.1 Update active docs such as `README.md`, `AGENTS.md`, and `docs/mires-skill-architecture.md` to describe Codex-only behavior.
- [x] 3.2 Apply the `mires-namespace-distribution` spec delta so active requirements define Codex-only distribution and verification.

## 4. Rebuild Verification

- [x] 4.1 Update `scripts/verify-package.js` to validate only bundled Codex assets and to fail on stale active OpenCode product references.
- [x] 4.2 Run targeted searches and package verification to confirm active source files no longer expose OpenCode behavior while archived OpenSpec history remains unchanged.
