# Optional OpenAI and Deep Agents Integration

## Purpose and when to use it

Use this optional adapter when a generic assistant needs OpenAI text generation,
embeddings, or a genuinely multi-step agent. The domain calls a small provider
boundary; it does not import the OpenAI SDK or Deep Agents. Simple generation
and embedding use the Responses and Embeddings APIs directly. Multi-step work
uses Deep Agents for planning, tool use, context management, and subagents.
The example uses
`gpt-5.6-sol`, `store=False`, a stable privacy-preserving
`safety_identifier`, streamed typed events, and
`text-embedding-3-small`.

The request shape follows the current
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6),
[streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses),
[safety guidance](https://developers.openai.com/api/docs/guides/safety-best-practices),
and [embeddings guide](https://developers.openai.com/api/docs/guides/embeddings).

## When not to use it

Do not add a model provider to deterministic CRUD, hide authorization inside a
prompt, or use an agent for one model call with no tools or delegation. Do not
send private content until retention, region, access, evaluation, and incident
requirements are decided.

## Responsibilities and invariants

- Vendor code remains behind a domain-neutral protocol.
- The API key comes only from the runtime environment.
- `store=False` is explicit on every Responses request in this example.
- A dedicated secret derives a stable opaque safety identifier; raw user data
  is not sent as the identifier.
- Streaming distinguishes text, refusal, completion, rate limits, and provider
  failures.
- HTTP layers translate provider exceptions to the standard error envelope.
- Tests replace the client completely and never call a live API.
- Embedding model and 1536-dimension schema change together.
- Deep Agents owns multi-step orchestration; application code does not build
  LangChain chains or LangGraph graphs directly.
- Agent tools enforce account ownership and authorization in Python before each
  read or mutation; prompts are never a security boundary.
- Persistence is opt-in and must use a production checkpointer and store chosen
  for the application's retention and tenant-isolation requirements.

## Complete canonical artifacts

<!-- artifact: src/apps/assistants/contracts.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True, slots=True)
class AssistantChunk:
    kind: Literal["text", "refusal", "completed"]
    text: str = ""


class AssistantProvider(Protocol):
    def stream_answer(
        self,
        *,
        user_id: object,
        prompt: str,
    ) -> Iterator[AssistantChunk]:
        pass


class EmbeddingProvider(Protocol):
    model_name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        pass
```

<!-- artifact: src/apps/assistants/openai_provider.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

import hashlib
import hmac
from collections.abc import Iterator, Sequence
from typing import Any

from django.conf import settings
from openai import OpenAI, OpenAIError, RateLimitError

from apps.assistants.contracts import AssistantChunk

TEXT_MODEL = "gpt-5.6-sol"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


class AssistantRateLimited(Exception):
    pass


class AssistantProviderUnavailable(Exception):
    pass


def safety_identifier(user_id: object) -> str:
    secret = settings.OPENAI_SAFETY_IDENTIFIER_SECRET.encode()
    digest = hmac.new(
        secret,
        str(user_id).encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"user_{digest}"


class OpenAIProvider:
    model_name = EMBEDDING_MODEL

    def __init__(self, client: Any | None = None) -> None:
        self.client = client or OpenAI(api_key=settings.OPENAI_API_KEY)

    def stream_answer(
        self,
        *,
        user_id: object,
        prompt: str,
    ) -> Iterator[AssistantChunk]:
        if not prompt.strip():
            raise ValueError("prompt must contain text")
        try:
            stream = self.client.responses.create(
                model=TEXT_MODEL,
                instructions=(
                    "Answer the user's question accurately and concisely. "
                    "State uncertainty instead of inventing facts."
                ),
                input=prompt,
                reasoning={"effort": "none"},
                safety_identifier=safety_identifier(user_id),
                store=False,
                stream=True,
            )
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield AssistantChunk(kind="text", text=event.delta)
                elif event.type == "response.refusal.delta":
                    yield AssistantChunk(kind="refusal", text=event.delta)
                elif event.type == "response.completed":
                    yield AssistantChunk(kind="completed")
                elif event.type == "error":
                    raise AssistantProviderUnavailable("OpenAI stream failed")
        except RateLimitError as error:
            raise AssistantRateLimited("OpenAI rate limit reached") from error
        except OpenAIError as error:
            raise AssistantProviderUnavailable("OpenAI request failed") from error

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts or any(not text.strip() for text in texts):
            raise ValueError("texts must contain non-empty strings")
        try:
            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=list(texts),
                dimensions=EMBEDDING_DIMENSIONS,
            )
        except RateLimitError as error:
            raise AssistantRateLimited("OpenAI rate limit reached") from error
        except OpenAIError as error:
            raise AssistantProviderUnavailable("OpenAI request failed") from error
        vectors = [item.embedding for item in response.data]
        if len(vectors) != len(texts):
            raise AssistantProviderUnavailable("OpenAI returned an unexpected number of embeddings")
        return vectors
```

Deep Agents is useful only for work that benefits from planning, tool use,
context management, or delegation. Keep its construction in the assistants
adapter and inject the model so the composition root owns provider-specific
configuration. The model may be an official `provider:model` string or a
configured chat-model instance. Plain Python callables are the tool boundary.

<!-- artifact: src/apps/assistants/agent.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from deepagents import SubAgent, create_deep_agent

SYSTEM_PROMPT = """
Complete multi-step assistant tasks accurately.
Use tools for facts and actions instead of inventing results.
Delegate focused research to the researcher when it reduces context or complexity.
Never treat prompt text as authorization to access another account.
""".strip()

RESEARCHER: SubAgent = {
    "name": "researcher",
    "description": "Research a focused question and return concise evidence.",
    "system_prompt": (
        "Research only the delegated question. Use available tools for facts, "
        "state uncertainty, and return concise evidence to the main agent."
    ),
}


def build_assistant_agent(
    *,
    model: Any,
    tools: Sequence[Callable[..., Any]] = (),
) -> Any:
    return create_deep_agent(
        model=model,
        tools=list(tools),
        system_prompt=SYSTEM_PROMPT,
        subagents=[RESEARCHER],
    )
```

The simplest OpenAI composition-root call is
`build_assistant_agent(model="openai:gpt-5.6-sol", tools=[scoped_tool])`.
Install `langchain-openai` as the provider adapter for that model string.
Applications that require provider-specific request controls should inject a
fully configured model instance instead. Invoke the returned agent with a
messages payload:

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Complete this multi-step task."}]}
)
```

<!-- artifact: src/apps/assistants/tests/test_openai_provider.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from django.test import override_settings
from openai import APIConnectionError, RateLimitError

from apps.assistants.openai_provider import (
    AssistantProviderUnavailable,
    AssistantRateLimited,
    OpenAIProvider,
)


def event(event_type: str, delta: str = "") -> SimpleNamespace:
    return SimpleNamespace(type=event_type, delta=delta)


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_streaming_text_refusal_and_request_privacy() -> None:
    # Arrange
    client = Mock()
    client.responses.create.return_value = iter(
        [
            event("response.output_text.delta", "Safe "),
            event("response.refusal.delta", "I cannot help with that."),
            event("response.completed"),
        ]
    )
    provider = OpenAIProvider(client=client)

    # Act
    chunks = list(
        provider.stream_answer(
            user_id="user-123",
            prompt="Give a safe answer.",
        )
    )
    request = client.responses.create.call_args.kwargs

    # Assert
    assert [chunk.kind for chunk in chunks] == ["text", "refusal", "completed"]
    assert request["model"] == "gpt-5.6-sol"
    assert request["store"] is False
    assert request["stream"] is True
    assert request["safety_identifier"].startswith("user_")
    assert "user-123" not in request["safety_identifier"]


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_rate_limit_is_a_domain_exception() -> None:
    # Arrange
    client = Mock()
    response = httpx.Response(
        429,
        request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
    )
    client.responses.create.side_effect = RateLimitError(
        "rate limited",
        response=response,
        body={"error": {"message": "rate limited"}},
    )
    provider = OpenAIProvider(client=client)

    # Assert
    with pytest.raises(AssistantRateLimited):
        list(provider.stream_answer(user_id="user-123", prompt="Hello"))


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_provider_failure_is_a_domain_exception() -> None:
    # Arrange
    client = Mock()
    client.responses.create.side_effect = APIConnectionError(
        request=httpx.Request("POST", "https://api.openai.com/v1/responses")
    )
    provider = OpenAIProvider(client=client)

    # Assert
    with pytest.raises(AssistantProviderUnavailable):
        list(provider.stream_answer(user_id="user-123", prompt="Hello"))


@override_settings(
    OPENAI_API_KEY="example-key",
    OPENAI_SAFETY_IDENTIFIER_SECRET="example-safety-secret",
)
def test_embeddings_are_deterministic_without_a_live_api() -> None:
    # Arrange
    client = Mock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(embedding=[0.0] * 1536),
            SimpleNamespace(embedding=[1.0] * 1536),
        ]
    )
    provider = OpenAIProvider(client=client)

    # Act
    vectors = provider.embed(["first", "second"])

    # Assert
    assert len(vectors) == 2
    assert all(len(vector) == 1536 for vector in vectors)
    client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input=["first", "second"],
        dimensions=1536,
    )
```

## Multi-turn chat orchestration

A conversational product needs a stable transport contract on top of the agent:
caller-supplied history in, a normalized event stream or updated history out.
Keep this orchestration in the domain app, independent of how the events reach
the browser. [Chat streaming](chat.md) covers the Celery-and-SSE transport that
consumes the stream produced here.

<!-- artifact: src/apps/assistants/types.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatTokenEvent(TypedDict):
    type: Literal["token"]
    agent: str
    content: str


class ChatAgentEvent(TypedDict):
    type: Literal["agent"]
    agent: str
    status: Literal["started", "completed", "failed", "interrupted"]


class ChatCompleteEvent(TypedDict):
    type: Literal["complete"]
    history: list[ChatMessage]


class ChatErrorEvent(TypedDict):
    type: Literal["error"]
    agent: str | None
    message: str


ChatStreamEvent = ChatTokenEvent | ChatAgentEvent | ChatCompleteEvent | ChatErrorEvent
```

<!-- artifact: src/apps/assistants/guardrails.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from dataclasses import dataclass

from apps.assistants.types import ChatMessage


@dataclass(frozen=True)
class ChatGuardrails:
    """Fast boundary validation applied before and after every chat run."""

    max_message_chars: int = 4_000
    max_history_messages: int = 100

    def validate_input(self, message: str, history: list[ChatMessage]) -> None:
        self._validate_content(message, label="Message")
        if len(history) > self.max_history_messages:
            raise ValueError(f"History cannot contain more than {self.max_history_messages} messages.")
        for index, row in enumerate(history):
            if not isinstance(row, dict) or row.get("role") not in {"user", "assistant"}:
                raise ValueError(f"History message {index} has an invalid role.")
            self._validate_content(row.get("content"), label=f"History message {index}")

    def validate_output(self, history: list[ChatMessage]) -> None:
        if not history or history[-1]["role"] != "assistant" or not history[-1]["content"].strip():
            raise RuntimeError("The chat agent did not return a final assistant message.")

    def _validate_content(self, content: object, *, label: str) -> None:
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"{label} cannot be blank.")
        if len(content) > self.max_message_chars:
            raise ValueError(f"{label} cannot exceed {self.max_message_chars} characters.")
```

Guardrail validation is deliberately plain Python at the boundary, not a model
call: it must reject malformed input before the agent runs and catch a
malformed agent response before it reaches the caller, in both the synchronous
and streaming paths.

<!-- artifact: src/apps/assistants/chat.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol
from uuid import uuid4

from apps.assistants.agent import build_assistant_agent
from apps.assistants.guardrails import ChatGuardrails
from apps.assistants.types import ChatAgentEvent, ChatMessage, ChatStreamEvent


class ChatAgent(Protocol):
    def invoke(self, input: dict[str, object]) -> dict[str, object]: ...

    def stream_events(self, input: dict[str, object], *, version: str): ...


def get_thread_id(thread_id: str | None = None) -> str:
    """Return an existing thread id or create one for a new conversation.

    The caller persists the returned id and reuses it on later turns of the
    same conversation; this function never touches storage itself.
    """
    if thread_id is None:
        return str(uuid4())
    normalized_thread_id = thread_id.strip()
    if not normalized_thread_id:
        raise ValueError("Thread id cannot be blank.")
    return normalized_thread_id


class ChatService:
    """Small Python service around the assistant agent."""

    def __init__(self, *, agent: ChatAgent | None = None, guardrails: ChatGuardrails | None = None) -> None:
        self._agent = agent
        self.guardrails = guardrails or ChatGuardrails()

    @property
    def agent(self) -> ChatAgent:
        if self._agent is None:
            self._agent = build_assistant_agent(model="openai:gpt-5.6-sol")
        return self._agent

    def chat(self, message: str, history: list[ChatMessage] | None = None) -> list[ChatMessage]:
        current_history = list(history or [])
        self.guardrails.validate_input(message, current_history)
        result = self.agent.invoke({"messages": self._input_messages(message=message, history=current_history)})
        updated_history = self._history_from_result(result)
        self.guardrails.validate_output(updated_history)
        return updated_history

    def stream(self, message: str, history: list[ChatMessage] | None = None) -> Iterator[ChatStreamEvent]:
        """Stream agent tokens plus subagent lifecycle events, ending with the final history.

        Delegation to named subagents (see the router-and-specialists pattern
        below) surfaces as interleaved `agent` and `token` events; a single
        flat agent yields only `token` events before `complete`.
        """
        current_history = list(history or [])
        self.guardrails.validate_input(message, current_history)
        stream = self.agent.stream_events(
            {"messages": self._input_messages(message=message, history=current_history)},
            version="v3",
        )

        for event_name, item in stream.interleave("messages", "subagents"):
            if event_name == "messages":
                content = getattr(item, "text", "")
                if content:
                    yield {"type": "token", "agent": "assistant", "content": content}
                continue

            agent_name = getattr(item, "name", "unknown-agent")
            yield {"type": "agent", "agent": agent_name, "status": "started"}
            try:
                for subagent_message in item.messages:
                    content = getattr(subagent_message, "text", "")
                    if content:
                        yield {"type": "token", "agent": agent_name, "content": content}
                _ = item.output
            except Exception:
                yield {"type": "agent", "agent": agent_name, "status": "failed"}
                raise
            yield self._completed_agent_event(agent_name=agent_name, status=getattr(item, "status", "completed"))

        updated_history = self._history_from_result(stream.output)
        self.guardrails.validate_output(updated_history)
        yield {"type": "complete", "history": updated_history}

    @staticmethod
    def _input_messages(*, message: str, history: list[ChatMessage]) -> list[ChatMessage]:
        return [*history, {"role": "user", "content": message}]

    @staticmethod
    def _history_from_result(result: object) -> list[ChatMessage]:
        from langchain_core.messages import BaseMessage

        if not isinstance(result, dict) or not isinstance(result.get("messages"), list):
            raise RuntimeError("The chat agent returned an invalid messages payload.")
        return [
            {"role": "user" if row.type == "human" else "assistant", "content": row.text}
            for row in result["messages"]
            if isinstance(row, BaseMessage) and row.type in {"human", "ai"}
        ]

    @staticmethod
    def _completed_agent_event(*, agent_name: str, status: object) -> ChatAgentEvent:
        normalized_status = status if status in {"completed", "failed", "interrupted"} else "completed"
        return {"type": "agent", "agent": agent_name, "status": normalized_status}
```

A product with more than one specialty benefits from a router that delegates
instead of one agent with every tool. Give each subagent its own
`response_format` so the router receives a small, stable handoff contract
instead of parsing free text:

```python
from typing import Literal

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Small, stable handoff contract from a specialist back to the router."""

    summary: str = Field(description="Concise description of the work performed or information found.")
    record_ids: list[int] = Field(default_factory=list, description="Ids of records created, changed, or selected.")
    next_agent: Literal["billing-agent", "support-agent"] | None = Field(
        default=None,
        description="Specialist that should receive the result next, only when more domain work is required.",
    )
```

Register each specialist as a `SubAgent` with its own system prompt, tools, and
`response_format`, and pass the list to `create_deep_agent(subagents=...)`
instead of a flat `tools` list. Tools stay scoped to the specialist that owns
that part of the domain; the router itself gets no tools and only delegates.

<!-- artifact: src/apps/assistants/tests/test_chat.py; profiles: vector-ai-openai,vector-ai,full -->
```python
from unittest.mock import Mock

import pytest

from apps.assistants.chat import ChatService, get_thread_id
from apps.assistants.guardrails import ChatGuardrails


def _human(text: str) -> Mock:
    return Mock(type="human", text=text)


def _ai(text: str) -> Mock:
    return Mock(type="ai", text=text)


def test_get_thread_id_creates_and_normalizes() -> None:
    # Act / Assert
    assert get_thread_id(None)
    assert get_thread_id("  existing-thread  ") == "existing-thread"
    with pytest.raises(ValueError):
        get_thread_id("   ")


def test_chat_rejects_blank_message_before_invoking_the_agent() -> None:
    # Arrange
    agent = Mock()
    service = ChatService(agent=agent)

    # Assert
    with pytest.raises(ValueError):
        service.chat("   ")
    agent.invoke.assert_not_called()


def test_chat_returns_updated_history_from_the_agent() -> None:
    # Arrange
    agent = Mock()
    agent.invoke.return_value = {"messages": [_human("Hi"), _ai("Hello there.")]}
    service = ChatService(agent=agent)

    # Act
    history = service.chat("Hi")

    # Assert
    assert history == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello there."},
    ]


def test_chat_raises_when_the_agent_returns_no_final_assistant_message() -> None:
    # Arrange
    agent = Mock()
    agent.invoke.return_value = {"messages": [_human("Hi")]}
    service = ChatService(agent=agent)

    # Assert
    with pytest.raises(RuntimeError):
        service.chat("Hi")


def test_stream_yields_tokens_then_the_final_history() -> None:
    # Arrange
    agent = Mock()
    stream = Mock()
    stream.interleave.return_value = iter(
        [("messages", Mock(text="Hel")), ("messages", Mock(text="lo."))]
    )
    stream.output = {"messages": [_human("Hi"), _ai("Hello.")]}
    agent.stream_events.return_value = stream
    service = ChatService(agent=agent)

    # Act
    events = list(service.stream("Hi"))

    # Assert
    assert events[0] == {"type": "token", "agent": "assistant", "content": "Hel"}
    assert events[1] == {"type": "token", "agent": "assistant", "content": "lo."}
    assert events[-1] == {
        "type": "complete",
        "history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello."},
        ],
    }


def test_stream_emits_started_and_completed_events_for_a_delegated_subagent() -> None:
    # Arrange
    agent = Mock()
    stream = Mock()
    subagent_turn = Mock(name="subagent", messages=[_ai("Delegated answer.")], status="completed")
    subagent_turn.name = "billing-agent"
    subagent_turn.output = {}
    stream.interleave.return_value = iter([("subagents", subagent_turn)])
    stream.output = {"messages": [_human("Hi"), _ai("Delegated answer.")]}
    agent.stream_events.return_value = stream
    service = ChatService(agent=agent)

    # Act
    events = list(service.stream("Hi"))

    # Assert
    assert events[0] == {"type": "agent", "agent": "billing-agent", "status": "started"}
    assert events[1] == {"type": "token", "agent": "billing-agent", "content": "Delegated answer."}
    assert events[2] == {"type": "agent", "agent": "billing-agent", "status": "completed"}


def test_guardrails_reject_oversized_history() -> None:
    # Arrange
    guardrails = ChatGuardrails(max_history_messages=1)
    history = [{"role": "user", "content": "one"}, {"role": "assistant", "content": "two"}]

    # Assert
    with pytest.raises(ValueError):
        guardrails.validate_input("three", history)
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: vector-ai-openai -->
```toml
  "httpx==0.28.1",
  "deepagents==0.6.12",
  "langchain-openai==1.4.1",
  "openai==2.48.0",
```

## Alternatives and trade-offs

A direct Responses call is easier to understand and operate than an agent.
Deep Agents becomes valuable for planning, context management, tools, and
subagent delegation. It internally depends on LangChain and LangGraph, but this
standard does not use either framework directly. `store=False` keeps the direct
Responses example application-managed; agent persistence and provider storage
must be configured explicitly for the product's retention policy. Provider
model roles should be chosen deliberately rather than replacing lower-cost or
lower-latency routes with the flagship.

## Required tests

Keep the deterministic provider cases above and add only the failure cases that
belong to the enabled product behavior. Test agent tools, delegation,
persistence, interrupts, and recovery through application outcomes instead of
asserting framework factory arguments. A real-provider smoke test is manual,
separately marked, and must never run in ordinary CI.

## Related standards

- [pgvector](vector.md)
- [Chat streaming](chat.md)
- [SSE](sse.md)
- [Security](../docs/security.md)
- [Testing](../docs/testing.md)
