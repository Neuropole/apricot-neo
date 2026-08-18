"""Groq model provider implementation."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import APIError, Groq

from apricot.models.base import (
    BaseProvider,
    Message,
    ModelAPIError,
    ModelConfigError,
    ModelResponse,
    ModelResponseError,
    Role,
    TokenUsage,
    ToolCall,
    ToolDefinition,
)


class GroqProvider(BaseProvider):
    """LLM Provider backed by the Groq API."""

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = DEFAULT_MODEL,
        client: Groq | None = None,
    ) -> None:
        """Initialize the Groq provider.

        Args:
            api_key: Optional API key. If not provided, reads from GROQ_API_KEY environment.
            default_model: Default Groq model identifier to use when none is specified.
            client: Optional pre-configured Groq client (primarily for testing/mocking).

        Raises:
            ModelConfigError: If no API key is supplied or found in the environment.
        """
        self.default_model = default_model

        if client is not None:
            self._client = client
            return

        resolved_key = api_key
        if not resolved_key:
            load_dotenv()
            resolved_key = os.environ.get("GROQ_API_KEY")

        if not resolved_key:
            raise ModelConfigError(
                "GROQ_API_KEY is not set. Please provide it via constructor argument "
                "or set the GROQ_API_KEY environment variable in your .env file."
            )

        self._client = Groq(api_key=resolved_key)

    def _convert_message(self, message: Message) -> dict[str, Any]:
        """Convert a generic Message instance into Groq-compatible message dictionary."""
        role_str = message.role_value

        if role_str in (Role.SYSTEM.value, Role.USER.value):
            return {
                "role": role_str,
                "content": message.content or "",
            }

        if role_str == Role.ASSISTANT.value:
            payload: dict[str, Any] = {"role": "assistant"}
            if message.content is not None:
                payload["content"] = message.content
            if message.tool_calls:
                payload["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": (
                                tc.raw_arguments
                                if tc.raw_arguments is not None
                                else json.dumps(tc.arguments)
                            ),
                        },
                    }
                    for tc in message.tool_calls
                ]
            return payload

        if role_str == Role.TOOL.value:
            tool_payload: dict[str, Any] = {
                "role": "tool",
                "tool_call_id": message.tool_call_id or "",
                "content": message.content or "",
            }
            if message.name:
                tool_payload["name"] = message.name
            return tool_payload

        # Fallback for custom/unsupported roles
        return {
            "role": role_str,
            "content": message.content or "",
        }

    def _convert_tool(self, tool: ToolDefinition) -> dict[str, Any]:
        """Convert a generic ToolDefinition into Groq function tool schema."""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ModelResponse:
        """Generate a completion using Groq chat completions API.

        Args:
            messages: List of chat messages.
            tools: Optional list of tools to provide to the model.
            model: Model identifier override.
            temperature: Optional sampling temperature.
            max_tokens: Optional token limit on generation.

        Returns:
            Standardized ModelResponse.

        Raises:
            ModelAPIError: If the Groq API call fails.
            ModelResponseError: If the response is malformed.
        """
        groq_messages = [self._convert_message(m) for m in messages]
        chosen_model = model or self.default_model

        kwargs: dict[str, Any] = {
            "model": chosen_model,
            "messages": groq_messages,
        }

        if tools:
            kwargs["tools"] = [self._convert_tool(t) for t in tools]
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        try:
            raw_response = self._client.chat.completions.create(**kwargs)
        except APIError as exc:
            raise ModelAPIError(f"Groq API error: {exc.message}") from exc
        except Exception as exc:
            raise ModelAPIError(f"Unexpected error communicating with Groq API: {exc}") from exc

        try:
            choice = raw_response.choices[0]
            choice_message = choice.message

            tool_calls: list[ToolCall] = []
            if choice_message.tool_calls:
                for tc in choice_message.tool_calls:
                    tool_calls.append(
                        ToolCall.from_raw(
                            id=tc.id,
                            name=tc.function.name,
                            raw_arguments=tc.function.arguments,
                        )
                    )

            usage: TokenUsage | None = None
            if raw_response.usage:
                usage = TokenUsage(
                    prompt_tokens=raw_response.usage.prompt_tokens or 0,
                    completion_tokens=raw_response.usage.completion_tokens or 0,
                    total_tokens=raw_response.usage.total_tokens or 0,
                )

            return ModelResponse(
                content=choice_message.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
                usage=usage,
                model=raw_response.model,
            )
        except (IndexError, AttributeError) as exc:
            raise ModelResponseError(f"Malformed response from Groq API: {exc}") from exc
