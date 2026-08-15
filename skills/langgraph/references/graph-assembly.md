---
name: graph-assembly
description: "Mires LangGraph graph-assembly guidance. Use for StateGraph setup, explicit node names, START/END wiring, compile boundaries, and injected graph dependencies."
---

# LangGraph Graph Assembly

Use this skill when building or refactoring the graph wiring layer.

## Rules

- Build graphs with `StateGraph(<TypedDictState>)`.
- Add nodes with explicit names.
- Keep the required base flow simple, such as `START -> get_customer_orders -> END`.
- If an LLM step is needed, add it as a separate node after the service-backed node.
- Inject dependencies such as model instances into node factories or graph builders; do not use globals.
- Return `graph.compile()` from the graph builder.
