# Agent instructions

## Purpose

Maintain this repository as a concise, Markdown-only standards reference. It is
not a scaffold, starter kit, or product-specific codebase.

## Invariants

- Track only files whose names end in `.md`.
- Put every executable artifact behind exactly one canonical marker and one
  complete fenced block.
- Use repository-relative, traversal-safe target paths.
- Keep every target/profile pair unique.
- Keep `source-map.md` synchronized with every reconstructed target.
- Never commit generated or reconstructed source.
- Never put credentials, tokens, private URLs, or customer data in examples.
- Do not use omitted sections, placeholder ellipses, or pseudocode in
  canonical fences.
- Do not add tests, test-only documentation, test dependencies, test scripts,
  test configuration, mocks, or test artifacts.

## Architecture

- Prefer Server Components and keep `"use client"` at the smallest interactive
  boundary.
- Keep route files thin and product behavior in feature modules.
- Separate reusable visual primitives from domain features.
- Validate all external input and API output at runtime.
- Enforce authentication and authorization on the server.
- Prefer URL state for shareable navigation state.
- Make pending, empty, error, retry, and mutation outcomes explicit.
- Do not add global state or abstraction layers without a demonstrated need.

## Graphify

This repository has a generated knowledge graph in `graphify-out/`. Keep that
directory untracked.

- For handbook architecture, ownership, or cross-document questions, run
  `graphify query "<question>"` before broad raw-file searches when
  `graphify-out/graph.json` exists.
- Use `graphify path "<A>" "<B>"` to inspect relationships and
  `graphify explain "<concept>"` for a focused concept.
- Use `graphify-out/wiki/index.md` for broad graph navigation when it exists.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or
  when focused graph commands do not provide enough context.
- After changing canonical Markdown, run `graphify extract .` to refresh
  documentation semantics. `graphify update .` alone is insufficient because
  it only re-extracts code.
- Never stage or commit anything under `graphify-out/`.

## Change protocol

1. Read the owning document and `source-map.md`.
2. Update prose, complete artifacts, and source-map ownership together.
3. Bootstrap the reconstructor and run its `--validate` mode.
4. Materialize all affected profiles into fresh external empty directories.
5. Run each affected profile's documented checks.
6. Refresh Graphify with `graphify extract .`.
7. Run `git diff --check` and verify every tracked path ends in `.md`.

Do not commit or push unless the user explicitly asks.
