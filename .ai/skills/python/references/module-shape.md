---
name: module-shape
description: "Mires Python module-organization guidance. Use for small modules, public entry points, helper placement, extraction decisions, import style, and concise docstrings."
---

# Python Module Shape

Use this skill when creating a module, splitting a file, or cleaning up Python organization.

## Rules

- Start with the smallest useful module.
- Keep public entry points near the top and helpers below them.
- Extract a new file when a module mixes unrelated responsibilities or becomes hard to scan.
- Reuse the repo package layout, import grouping, naming, and error model when those conventions already exist.
- Add short docstrings where they clarify a public API or a non-obvious rule.
