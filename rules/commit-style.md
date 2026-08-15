# Commit Style

Write short imperative commit subjects describing the change, for example `add celery retry rules` or `update python testing reference`.

## Rules

- Use the imperative mood: `add`, `update`, `fix`, `remove`, not `added` or `adding`.
- Keep the subject under roughly 72 characters and lowercase after the first word.
- Explain why in the body when the reason is not obvious from the diff.
- Keep a commit scoped to one intent; split unrelated changes.
- Do not commit generated runtime output such as installed Codex or OpenCode trees.

## Pull Requests

Summarize which catalog entries changed, explain why the change is needed, and list the manual validation performed.
