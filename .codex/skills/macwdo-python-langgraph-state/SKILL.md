---
name: macwdo-python-langgraph-state
description: "Macwdo LangGraph state guidance. Use for TypedDict workflow state, orchestration-only fields, concrete types, error fields, messages, and immutable state updates."
---

# LangGraph State

Use this skill when defining or refactoring LangGraph workflow state.

## Rules

- Use `TypedDict` for graph state.
- Include only orchestration data in state.
- Add `error: str | None` when nodes need to persist failures.
- Prefer concrete types such as `list[str]` or `list[BaseMessage]`.
- Return `{**state, ...}` updates instead of mutating the incoming state.
