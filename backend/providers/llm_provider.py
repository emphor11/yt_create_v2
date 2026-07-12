from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable


LLMMessageRole = Literal["system", "user", "assistant"]


class LLMProviderError(Exception):
    """Raised when an LLM provider cannot return a usable response."""


@dataclass(frozen=True)
class LLMMessage:
    role: LLMMessageRole
    content: str


@dataclass(frozen=True)
class LLMJsonRequest:
    messages: list[LLMMessage]
    schema_name: str
    response_schema: dict[str, Any] | None = None
    temperature: float = 0.2
    max_tokens: int = 1200


@dataclass(frozen=True)
class LLMProviderMetadata:
    provider: str
    model: str
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMJsonResponse:
    payload: dict[str, Any]
    metadata: LLMProviderMetadata


@runtime_checkable
class LLMProvider(Protocol):
    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        """Return JSON payload for a structured request."""
