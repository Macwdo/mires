---
name: service-node-pattern
description: "Mires canonical LangGraph service-node pattern. Use when implementing the full state, services, node factory, graph setup, and extension pattern for multiple service-backed nodes."
---

# LangGraph Service Node Pattern

Use this skill when the task asks for a complete reusable LangGraph pattern.

## Rules

- Split implementation into `state.py`, `services.py`, `node_factory.py`, and `graph.py` unless the repo has a different local module shape.
- Keep state typed with `TypedDict` and optional `messages` and `error` fields when needed.
- Put domain functions in services and keep them graph-independent.
- Create service-backed nodes through the reusable node factory.
- Wire nodes in `StateGraph` with explicit names and edges.
- Scale by adding state fields, service functions, input mappers, and node registrations without moving business logic into the graph layer.

## Checklist

- State is typed.
- Services are graph-independent.
- Nodes return fresh state.
- Graph dependencies are injected.
- LLM adapters are separate from business services.
