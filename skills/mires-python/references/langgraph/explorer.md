---
name: explorer
description: "Explore LangGraph reference categories inside the langgraph skill. Use when selecting the specific LangGraph reference files to load."
---

# LangGraph Explorer

Use this guide to select the specific LangGraph reference files needed for workflow code changes.

## Reference Categories

- State and contracts: `skills/mires-python/references/langgraph/state.md`
- Services: `skills/mires-python/references/langgraph/services.md`
- Node factories and LLM nodes: `skills/mires-python/references/langgraph/node-factory.md`, `skills/mires-python/references/langgraph/llm-nodes.md`
- Graph assembly and full workflow pattern: `skills/mires-python/references/langgraph/graph-assembly.md`, `skills/mires-python/references/langgraph/service-node-pattern.md`

## Selection Rules

- Start with state and services before loading node factory or graph assembly references.
- Use the service-node pattern reference for end-to-end examples.
- Keep graph orchestration thin and service-backed.
