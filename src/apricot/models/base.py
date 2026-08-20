"""Base provider-independent model abstraction and data structures."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Role(str, Enum):
    """Message roles for chat interactions."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class ToolCall:
    """Representation of a tool/function call requested by the model."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    raw_arguments: str | None = None

    @classmethod
    def from_raw(cls, id: str, name: str, raw_arguments: str) -> ToolCall:
        """Create a ToolCall from raw JSON arguments string."""
        arguments: dict[str, Any] = {}
        if raw_arguments:
            try:
                parsed = json.loads(raw_arguments)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in tool call arguments for '{name}': {raw_arguments}"
                ) from exc
            if not isinstance(parsed, dict):
                val_type = type(parsed).__name__
                raise ValueError(
                    f"Tool call arguments for '{name}' must be a JSON object, got {val_type}"
                )
            arguments = parsed
        return cls(id=id, name=name, arguments=arguments, raw_arguments=raw_arguments)


@dataclass(frozen=True)
class ToolDefinition:
    """Specification of a tool available to the model."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Universal chat message across all model providers."""

    role: Role | str
    content: str | None = None
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] | None = None

    @property
    def role_value(self) -> str:
        """Return the string value of the role."""
        return self.role.value if isinstance(self.role, Role) else str(self.role)

    @classmethod
    def system(cls, content: str) -> Message:
        """Construct a system message."""
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> Message:
        """Construct a user message."""
        return cls(role=Role.USER, content=content)

    @classmethod
    def assistant(
        cls, content: str | None = None, tool_calls: list[ToolCall] | None = None
    ) -> Message:
        """Construct an assistant message."""
        return cls(role=Role.ASSISTANT, content=content, tool_calls=tool_calls)

    @classmethod
    def tool_result(cls, tool_call_id: str, content: str, name: str | None = None) -> Message:
        """Construct a tool result message."""
        return cls(role=Role.TOOL, tool_call_id=tool_call_id, content=content, name=name)


@dataclass(frozen=True)
class TokenUsage:
    """Token consumption statistics for a model response."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ModelResponse:
    """Universal model response object."""

    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    model: str | None = None

    @property
    def has_tool_calls(self) -> bool:
        """Check whether the model requested one or more tool calls."""
        return bool(self.tool_calls)

    def to_message(self) -> Message:
        """Convert the model response into an assistant chat message."""
        return Message.assistant(
            content=self.content,
            tool_calls=self.tool_calls if self.has_tool_calls else None,
        )


class ModelError(Exception):
    """Base exception for model and provider errors."""


class ModelConfigError(ModelError):
    """Raised when provider configuration or credentials are missing or invalid."""


class ModelAPIError(ModelError):
    """Raised when an upstream provider API call fails."""


class ModelResponseError(ModelError):
    """Raised when the provider returns an unparseable or malformed response."""


class BaseProvider(ABC):
    """Abstract interface for all model providers (Groq, Ollama, etc.)."""

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ModelResponse:
        """Generate a completion for the provided messages and available tools.

        Args:
            messages: List of chat messages.
            tools: Optional list of tool definitions the model may invoke.
            model: Optional model identifier override.
            temperature: Optional sampling temperature.
            max_tokens: Optional token limit on generation.

        Returns:
            A standardized ModelResponse instance.

        Raises:
            ModelConfigError: If credentials or setup are missing.
            ModelAPIError: If the provider API request fails.
            ModelResponseError: If the response cannot be parsed.
        """
