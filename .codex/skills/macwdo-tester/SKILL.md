---
name: macwdo-tester
description: "Macwdo local app verification agent. Use to test routed local app flows with linked-worktree awareness, portless dev-server routing, agent-browser verification, and concise pass/fail reporting."
---

# Macwdo Tester

Use this skill when a user asks to test or verify a local app flow with Macwdo conventions.

This is a workflow skill. Load `portless` for routed local dev-server command details and `agent-browser` for browser automation command details instead of duplicating those references here.

## Workflow

1. Inspect the request and repo context.
   - Identify the scenario, app directory, package manager, likely startup command, and expected success state.
   - Check for existing user instructions, test notes, environment setup, and URL-sensitive settings such as `.env`, `.env.local`, callbacks, redirects, CORS, allowed hosts, base URLs, frontend URLs, and backend URLs.

2. Validate linked-worktree context when applicable.
   - Run `git rev-parse --git-dir`.
   - If the result indicates `/worktrees/`, include the branch or worktree context in the final report.
   - If the current directory is not a linked worktree, report that fact before proceeding. Continue only when the user requested verification in the current checkout or no linked-worktree requirement applies.

3. Prepare portless.
   - Load and follow the `portless` skill for command-level details.
   - Verify `portless` is available.
   - Choose a startup command only when it is unambiguous from the repo or user request.
   - Start the app through portless, using a named route when the user or repo provides one.
   - Do not guess raw localhost ports. Use the routed `.localhost` URL returned by portless.
   - Stop before browser work if a routed URL cannot be established, and report the concrete blocker.

4. Verify with agent-browser.
   - Load and follow the `agent-browser` skill for command-level details.
   - Open the routed URL and wait for a usable state.
   - Take a baseline snapshot before interacting.
   - Use a snapshot -> interact -> wait -> verify loop.
   - After any interaction that changes page state, URL, network state, or DOM, wait and refresh browser context with a new snapshot before continuing.
   - Verify expected URL transitions, expected text or controls, saved state, and absence of unexpected errors.

5. Stop at the first real blocker.
   - Do not continue clicking after an expected control, route, text, or successful state is missing after appropriate waiting.
   - Capture the first concrete blocker, the step where it happened, and any relevant visible page state.

6. Report and clean up.
   - Stop any dev server you started unless the user asked to keep it running.
   - Final reports must include the scenario tested, pass/fail/blocked result, branch or worktree context when available, routed URL used, first blocker when failing, and dev-server shutdown status.
   - Keep the report concise and execution-focused.

## Guardrails

- Do not use raw localhost guesses for browser verification.
- Do not skip the baseline snapshot.
- Do not continue a scenario after a concrete failure invalidates it.
- Do not leave dev servers running unless asked.
- Do not claim a pass without verifying the expected outcome in the browser.
