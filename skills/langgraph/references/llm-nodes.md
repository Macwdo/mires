---
name: llm-nodes
description: "Mires LangGraph LLM-node guidance. Use for ChatOpenAI/BaseChatModel injection, reading state messages, appending model responses immutably, and matching service-node error handling."
---

# LangGraph LLM Nodes

Use this skill when a LangGraph workflow includes LangChain messages or chat models.

## Rules

- Accept a `BaseChatModel` or `ChatOpenAI` instance as a parameter.
- Read from `state["messages"]`.
- Call `llm.invoke(state["messages"])`.
- Append the model response into a new `messages` list.
- Reuse the same `error` handling approach as service-backed nodes.
- Keep prompts and model dependencies outside global module state.
