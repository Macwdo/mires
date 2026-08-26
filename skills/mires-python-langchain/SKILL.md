---
name: mires-python-langchain
description: Apply Macwdo's Python standards to LangChain, LangGraph, Deep Agents, LLM integrations, document loaders, retrieval, persistence, tools, and agent testing. Use when building or reviewing Python applications in the LangChain ecosystem.
---

# Mires Python LangChain

Use this skill with `$mires-python`. Preserve the repository's configuration, dependency injection, persistence, service, error, and test boundaries; keep LangChain ecosystem code at explicit adapters instead of allowing framework objects to spread through the domain.

## Snippet-Driven Implementation

Always choose the closest snippet in this `SKILL.md` before generating LangChain ecosystem code: model initialization, structured output, agent, loader, splitter, LangGraph, persistence, or Deep Agent.

- Preserve typed inputs, injected models and clients, explicit state, bounded tools, authorization, and test seams shown by the snippet.
- Adapt provider packages, model names, sync/async APIs, checkpointers, and loader integrations to the versions installed by the repository.
- Verify changing APIs against official documentation before introducing a new import or argument.
- Do not combine snippets into a more complex runtime unless the workflow actually needs the combined capabilities.
- Use `$mires-python` snippets for ordinary services, settings, database access, Celery, and tests surrounding the agent boundary.

## Python Toolchain And Typing

Inherit `$mires-python` without exceptions: use `uv`, Ruff, `ty`, and pytest for every LangChain ecosystem project.

```bash
uv add langchain langgraph
uv add deepagents  # only when the harness is actually required
uv add --dev pytest ruff ty
uv sync

uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
```

- Add only the model, loader, vector-store, and checkpointer integration packages used by the project through `uv add`.
- Type model builders with `BaseChatModel`, loaders with `Iterable[Document]`, tools with concrete inputs and outputs, and graph state with `TypedDict`.
- Type graph nodes as state-to-update functions and services independently from LangGraph wiring.
- Keep provider payloads, model metadata, and tool JSON as `object` or narrowly scoped `Any` until validated.
- Do not let dynamic framework return types erase service and domain types.
- If an integration ships incomplete types, isolate a precise `# ty: ignore[rule-name]` at the adapter and keep the rest of the application typed.
- Do not add mypy or Pyright configuration beside `ty`.

## Choose The Smallest Runtime

- Use a chat model directly when the task is one prompt or one structured transformation.
- Use LangChain `create_agent` for a straightforward model-and-tools loop.
- Use LangGraph when state, branching, loops, persistence, streaming, interrupts, or human approval must be explicit.
- Use Deep Agents when the product needs an agent harness with planning, filesystem context, subagents, skills, or long-running multi-step work.
- Use retrieval only when external knowledge is required. Do not build a vector store around data that already has a reliable query interface.

Do not use Deep Agents for a simple tool call, or LangGraph for a linear model invocation. Framework choice must follow workflow complexity.

## Package And Configuration Rules

- Add only the provider integrations actually used by the project.
- Keep model name, provider, timeout, retry count, temperature, base URL, and tracing settings in the existing configuration surface.
- Read credentials only from environment-backed settings such as `OPENAI_API_KEY`; never place real values in code, examples, state, or tests.
- Inject initialized models, embeddings, vector stores, loaders, and clients at application boundaries.
- Do not initialize network clients at import time.
- Pin or lock dependency changes through the repository's package workflow and verify imports against the installed version.

## Chat Models

Prefer the standard model initializer when the application benefits from provider interchangeability:

```python
from __future__ import annotations

import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel


def build_chat_model() -> BaseChatModel:
    return init_chat_model(
        model=os.environ.get("MODEL_NAME", "openai:gpt-5.2"),
        temperature=0,
        timeout=30,
        max_retries=3,
    )
```

Use a concrete provider class when provider-specific behavior is intentional and tested. Accept `BaseChatModel` in services and graph builders so tests can inject a fake model.

For an OpenAI-compatible local or hosted endpoint, keep the endpoint and model configurable:

```python
model = init_chat_model(
    model=os.environ["MODEL_NAME"],
    model_provider="openai",
    base_url=os.environ["MODEL_BASE_URL"],
    api_key=os.environ.get("MODEL_API_KEY", "not-required"),
    temperature=0,
)
```

Never assume that OpenAI-compatible means every provider-specific field or response shape is identical. Test tool calling, structured output, streaming, and usage metadata against the actual endpoint.

## Structured Output

Use a typed schema instead of parsing prose when the result feeds application logic:

```python
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    category: str
    confidence: float = Field(ge=0, le=1)


classifier = model.with_structured_output(TicketClassification)
result = classifier.invoke("Customer cannot reset a password")
```

Validate structured output at the boundary. Do not expose raw provider response objects to domain code.

## LangChain Agents

Tools are typed functions with narrow inputs, useful docstrings, bounded side effects, and explicit authorization boundaries:

```python
from langchain.agents import create_agent


def lookup_order(order_id: str) -> str:
    """Return the current status of one order visible to the caller."""
    return f"Order {order_id} is processing"


agent = create_agent(
    model=model,
    tools=[lookup_order],
    system_prompt="Answer from tool results. Do not invent order status.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Where is order 123?"}]}
)
```

- Keep authorization and tenant scoping inside the tool boundary, not in the prompt alone.
- Pass scalar identifiers rather than ORM objects, sessions, or request objects.
- Separate read tools from mutating tools.
- Require explicit approval immediately before consequential mutations.
- Put business behavior in services and make tools thin adapters.
- Bound retries and tool loops; surface a typed failure when the stop condition is reached.

## Document Loaders

Document loaders normalize external sources into `Document` objects. Choose a loader by source and parser quality, not merely by file extension.

```python
from collections.abc import Iterable
from pathlib import Path

from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from langchain_core.documents import Document


def load_documents(path: Path) -> Iterable[Document]:
    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(path))
    elif path.suffix.lower() == ".csv":
        loader = CSVLoader(str(path))
    else:
        raise ValueError(f"Unsupported document type: {path.suffix}")

    yield from loader.lazy_load()
```

- Prefer `lazy_load()` for large corpora and `load()` only when bounded input comfortably fits memory.
- Preserve source, page, tenant, checksum, parser version, and access-control metadata.
- Validate that the parser produced useful text before indexing.
- Treat OCR, tables, layout, and scanned PDFs as parser-selection problems; use a layout-aware integration such as Docling when required.
- Keep ingestion idempotent with a stable document identity and content hash.
- Do not embed secrets, hidden fields, or content the requester is not authorized to retrieve.

## Splitting And Retrieval

Split based on semantic structure when available. Use recursive character splitting only as a safe default:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1_000,
    chunk_overlap=150,
    add_start_index=True,
)
chunks = splitter.split_documents(documents)
```

- Measure retrieval quality with representative queries before tuning chunk size.
- Store enough metadata to trace every answer back to the original source.
- Keep embedding model and vector dimension explicit and migration-aware.
- Filter by tenant and authorization before similarity ranking can expose a document.
- Make ingestion retries idempotent; do not duplicate chunks on replay.
- Prefer an existing database/search system when it already answers the query reliably.

## LangGraph

State is a typed contract. Nodes receive state, call injected services, and return narrow updates. Graph assembly owns orchestration, not business rules.

```python
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class WorkflowState(TypedDict):
    order_id: str
    status: str | None
    error: str | None


def load_status(state: WorkflowState) -> dict[str, str | None]:
    try:
        status = lookup_order(state["order_id"])
        return {"status": status, "error": None}
    except Exception as exc:
        return {"error": str(exc)}


builder = StateGraph(WorkflowState)
builder.add_node("load_status", load_status)
builder.add_edge(START, "load_status")
builder.add_edge("load_status", END)
graph = builder.compile()
```

- Use explicit node names and deterministic routing functions.
- Return updates instead of mutating the input state.
- Keep prompts and model instances outside module-global state.
- Use `Command` when one node must combine a state update with routing, and `Send` for deliberate fan-out.
- Stream at the application boundary; do not make core services depend on stream event formats.
- Test nodes as plain functions before testing the compiled graph path.

## Persistence And Threads

Compile with a checkpointer only when state must survive steps, interrupts, or invocations. Every persisted run needs a stable `thread_id`:

```python
from langgraph.checkpoint.memory import InMemorySaver


graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "example-thread"}}
result = graph.invoke(initial_state, config=config)
```

- Use `InMemorySaver` for tests and local experiments, not production durability.
- Use a database-backed sync or async saver that matches the application's I/O model in production.
- Distinguish thread-scoped checkpoints from long-term memory shared across threads.
- Namespace stored memory by user or tenant and apply deletion/retention requirements.
- Never serialize live database sessions, clients, file handles, or arbitrary secrets into graph state.

## Deep Agents

Deep Agents is a harness built on LangChain components and the LangGraph runtime. Use it when planning, filesystem context, subagents, skills, or long-running multi-step execution are actual product requirements.

```python
from deepagents import create_deep_agent


def search_knowledge(query: str) -> str:
    """Search the caller-authorized knowledge base."""
    return f"Results for {query}"


agent = create_deep_agent(
    model=model,
    tools=[search_knowledge],
    system_prompt="Research from tools, preserve citations, and state uncertainty.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Summarize the refund policy"}]}
)
```

- Give subagents narrow responsibilities and bounded tools.
- Choose a filesystem backend deliberately; sandbox or deny writes when execution is read-only.
- Require approval for external writes, messages, deployment, deletion, or financial actions.
- Keep skills and memory concise and scoped; do not use them as a secret store.
- Test stop conditions, tool denial, partial failure, resume behavior, and provenance.

## Error Handling And Observability

- Translate provider, parser, retrieval, tool, and checkpoint errors at their boundary.
- Distinguish retryable transport failures from invalid input and permanent domain failures.
- Bound retries with timeouts and backoff; do not permit infinite agent recovery loops.
- Trace model calls, tool calls, latency, token usage, retrieval hits, and graph transitions without recording secrets or private document contents.
- Log stable identifiers and failure categories rather than entire prompts or files by default.

## Testing

- Unit-test tools and services without a model.
- Use fake chat models or deterministic stubs for orchestration tests.
- Test structured-output validation failures.
- Test document loader metadata, empty extraction, idempotent ingestion, and access filters.
- Test LangGraph nodes independently, then one compiled happy path and meaningful branches.
- Test checkpointer resume with a stable `thread_id`.
- Keep a small provider integration suite behind explicit credentials; do not make ordinary unit tests call paid APIs.
- Evaluate realistic cases for correctness, grounding, tool choice, refusal, latency, and cost.

## Completion Checklist

- The chosen runtime is no more complex than the workflow requires.
- Models, clients, stores, and loaders are injected at boundaries.
- Tool inputs and outputs are typed and authorization is enforced in code.
- Documents retain provenance and access-control metadata.
- Graph state is typed, serializable, and free of live infrastructure objects.
- Persistence has an intentional thread and retention model.
- Failures, retries, approvals, and stop conditions are explicit.
- Focused tests and at least one realistic workflow path pass.

## Official References

- [LangChain models](https://docs.langchain.com/oss/python/langchain/models)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Document loaders](https://docs.langchain.com/oss/python/integrations/document_loaders/index)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
