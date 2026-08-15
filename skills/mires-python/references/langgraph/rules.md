# LangGraph

LangGraph patterns for typed state, service-backed nodes, graph assembly, and LLM integration.

## When To Use

Use for LangGraph state design, service-backed nodes, graph assembly, and LLM node patterns.

## Core Rules

- Inspect the existing workflow structure before editing.
- Keep business logic in services, not in graph wiring.
- Use typed state and explicit node ownership.

## Preferred Patterns

- Immutable state updates.
- Thin node adapters around domain services.
- Explicit graph assembly and node naming.

## Anti-Patterns

- Business logic buried in graph definitions.
- Untyped state blobs.
- Loading every LangGraph reference for a small local change.

## Checklist

- Identify the touched graph boundary.
- Confirm the current state and service patterns.
- Load only the relevant LangGraph references.
- Validate the changed workflow path.

## References Index

- `references/langgraph/explorer.md`
- `references/langgraph/state.md`
- `references/langgraph/services.md`
- `references/langgraph/node-factory.md`
- `references/langgraph/graph-assembly.md`
- `references/langgraph/llm-nodes.md`
- `references/langgraph/service-node-pattern.md`
