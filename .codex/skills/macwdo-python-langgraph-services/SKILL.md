---
name: macwdo-python-langgraph-services
description: "Macwdo LangGraph domain-service guidance. Use for keeping business logic outside graph definitions, service-backed nodes, dependency injection, and graph-independent service tests."
---

# LangGraph Services

Use this skill when a LangGraph node needs domain logic, database access, or external APIs.

## Rules

- Keep domain logic in service functions outside the graph layer.
- Do not put database access, API client setup, or business rules in graph definitions.
- Pass service dependencies into node factories or graph builders instead of using globals.
- Make service functions directly testable without compiling the graph.
- Use graph nodes as adapters that map state into service inputs and service outputs back into state.
