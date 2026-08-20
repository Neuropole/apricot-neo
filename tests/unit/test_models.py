"""Unit tests for model provider abstractions and GroqProvider."""

from unittest.mock import MagicMock, patch

import pytest
from groq import APIError

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
from apricot.models.groq import GroqProvider


class TestModelBaseStructures:
    """Test suite for base data models and interface contracts."""

    def test_message_constructors(self) -> None:
        """Test convenience factory methods for creating messages."""
        sys_msg = Message.system("System prompt")
        assert sys_msg.role == Role.SYSTEM
        assert sys_msg.content == "System prompt"
        assert sys_msg.role_value == "system"

        usr_msg = Message.user("Hello")
        assert usr_msg.role == Role.USER
        assert usr_msg.content == "Hello"

        asst_msg = Message.assistant("Response text")
        assert asst_msg.role == Role.ASSISTANT
        assert asst_msg.content == "Response text"

        tool_msg = Message.tool_result("call_123", "Result output", name="read_file")
        assert tool_msg.role == Role.TOOL
        assert tool_msg.tool_call_id == "call_123"
        assert tool_msg.content == "Result output"
        assert tool_msg.name == "read_file"

    def test_tool_call_parsing(self) -> None:
        """Test parsing raw JSON string arguments into ToolCall objects."""
        raw_json = '{"path": "src/main.py", "lines": 10}'
        tc = ToolCall.from_raw("call_1", "read_file", raw_json)
        assert tc.id == "call_1"
        assert tc.name == "read_file"
        assert tc.arguments == {"path": "src/main.py", "lines": 10}
        assert tc.raw_arguments == raw_json

        # Test with invalid JSON - should raise ValueError
        with pytest.raises(ValueError, match="Invalid JSON"):
            ToolCall.from_raw("call_2", "run_cmd", "invalid json")

        # Test with valid JSON that is not an object - should raise ValueError
        with pytest.raises(ValueError, match="must be a JSON object"):
            ToolCall.from_raw("call_3", "run_cmd", '["not", "a", "dict"]')

    def test_model_response_and_conversion(self) -> None:
        """Test ModelResponse properties and conversion to assistant Message."""
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        resp = ModelResponse(
            content="Hello world",
            finish_reason="stop",
            usage=usage,
            model="llama-3.3-70b-versatile",
        )
        assert not resp.has_tool_calls
        asst_msg = resp.to_message()
        assert asst_msg.role == Role.ASSISTANT
        assert asst_msg.content == "Hello world"
        assert asst_msg.tool_calls is None

        # Test with tool calls
        tc = ToolCall(id="c1", name="search", arguments={"query": "test"})
        resp_with_tools = ModelResponse(
            content=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
        )
        assert resp_with_tools.has_tool_calls
        asst_tool_msg = resp_with_tools.to_message()
        assert asst_tool_msg.tool_calls == [tc]

    def test_abstract_provider_contract(self) -> None:
        """Verify that BaseProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseProvider()  # type: ignore[abstract]


class TestGroqProvider:
    """Test suite for GroqProvider implementation."""

    def test_init_missing_api_key_raises_config_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify ModelConfigError is raised when no API key is provided or found."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        with patch("apricot.models.groq.load_dotenv"):
            with pytest.raises(ModelConfigError, match="GROQ_API_KEY is not set"):
                GroqProvider(api_key=None)

    def test_init_with_explicit_api_key(self) -> None:
        """Verify successful initialization when API key is explicitly passed."""
        with patch("apricot.models.groq.Groq") as mock_groq_cls:
            provider = GroqProvider(
                api_key="gsk_test_key_123",
                timeout=30.0,
                max_retries=3,
            )
            assert provider.default_model == "llama-3.3-70b-versatile"
            mock_groq_cls.assert_called_once_with(
                api_key="gsk_test_key_123",
                timeout=30.0,
                max_retries=3,
            )

    def test_generate_text_response(self) -> None:
        """Test standard text generation with mocked Groq client."""
        mock_client = MagicMock()
        mock_raw_choice = MagicMock()
        mock_raw_choice.message.content = "Here is the answer."
        mock_raw_choice.message.tool_calls = None
        mock_raw_choice.finish_reason = "stop"

        mock_raw_response = MagicMock()
        mock_raw_response.choices = [mock_raw_choice]
        mock_raw_response.model = "llama-3.3-70b-versatile"
        mock_raw_response.usage.prompt_tokens = 15
        mock_raw_response.usage.completion_tokens = 25
        mock_raw_response.usage.total_tokens = 40

        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        messages = [
            Message.system("System prompt"),
            Message.user("User question"),
        ]

        response = provider.generate(messages, temperature=0.7, max_tokens=100)

        assert response.content == "Here is the answer."
        assert not response.has_tool_calls
        assert response.finish_reason == "stop"
        assert response.model == "llama-3.3-70b-versatile"
        assert response.usage is not None
        assert response.usage.prompt_tokens == 15
        assert response.usage.completion_tokens == 25
        assert response.usage.total_tokens == 40

        mock_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User question"},
            ],
            temperature=0.7,
            max_tokens=100,
        )

    def test_generate_with_tool_definitions_and_tool_call_response(self) -> None:
        """Test tool schema passing and parsing model tool call response."""
        mock_client = MagicMock()
        mock_tc = MagicMock()
        mock_tc.id = "call_abc123"
        mock_tc.function.name = "read_file"
        mock_tc.function.arguments = '{"path": "src/config.py"}'

        mock_raw_choice = MagicMock()
        mock_raw_choice.message.content = None
        mock_raw_choice.message.tool_calls = [mock_tc]
        mock_raw_choice.finish_reason = "tool_calls"

        mock_raw_response = MagicMock()
        mock_raw_response.choices = [mock_raw_choice]
        mock_raw_response.model = "llama-3.3-70b-versatile"
        mock_raw_response.usage = None

        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        tools = [
            ToolDefinition(
                name="read_file",
                description="Read contents of a file",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            )
        ]

        messages = [
            Message.user("Read the file src/config.py"),
        ]

        response = provider.generate(messages, tools=tools)

        assert response.content is None
        assert response.has_tool_calls
        assert len(response.tool_calls) == 1
        tc = response.tool_calls[0]
        assert tc.id == "call_abc123"
        assert tc.name == "read_file"
        assert tc.arguments == {"path": "src/config.py"}

        # Verify tool schema was converted and passed correctly
        expected_tool_payload = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                },
            }
        ]
        mock_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Read the file src/config.py"}],
            tools=expected_tool_payload,
        )

    def test_generate_handles_tool_messages_and_assistant_history(self) -> None:
        """Test formatting assistant messages with tool calls and tool result messages."""
        mock_client = MagicMock()
        mock_raw_choice = MagicMock()
        mock_raw_choice.message.content = "File content processed."
        mock_raw_choice.message.tool_calls = None
        mock_raw_choice.finish_reason = "stop"

        mock_raw_response = MagicMock()
        mock_raw_response.choices = [mock_raw_choice]
        mock_raw_response.model = "llama-3.3-70b-versatile"
        mock_raw_response.usage = None

        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        tc = ToolCall.from_raw("call_1", "read_file", '{"path": "test.txt"}')
        messages = [
            Message.user("Please read test.txt"),
            Message.assistant(content=None, tool_calls=[tc]),
            Message.tool_result("call_1", "hello file content", name="read_file"),
        ]

        response = provider.generate(messages)
        assert response.content == "File content processed."

        mock_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Please read test.txt"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "read_file", "arguments": '{"path": "test.txt"}'},
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1",
                    "content": "hello file content",
                    "name": "read_file",
                },
            ],
        )

    def test_generate_api_error_handling(self) -> None:
        """Verify APIError is caught and raised as ModelAPIError."""
        mock_client = MagicMock()
        # Mock groq APIError
        err = APIError(
            message="Rate limit exceeded",
            request=MagicMock(),
            body=None,
        )
        mock_client.chat.completions.create.side_effect = err

        provider = GroqProvider(client=mock_client)
        with pytest.raises(ModelAPIError, match="Groq API error: Rate limit exceeded"):
            provider.generate([Message.user("Hello")])

    def test_generate_unexpected_error_handling(self) -> None:
        """Verify unexpected exception is wrapped into ModelAPIError."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = ConnectionError("Network unreachable")

        provider = GroqProvider(client=mock_client)
        with pytest.raises(ModelAPIError, match="Unexpected error communicating with Groq API"):
            provider.generate([Message.user("Hello")])

    def test_generate_malformed_response_handling(self) -> None:
        """Verify malformed choices list raises ModelResponseError."""
        mock_client = MagicMock()
        mock_raw_response = MagicMock()
        mock_raw_response.choices = []  # Empty choices list
        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        with pytest.raises(ModelResponseError, match="Malformed response from Groq API"):
            provider.generate([Message.user("Hello")])

    def test_generate_malformed_tool_call_arguments_handling(self) -> None:
        """Verify malformed tool call arguments string raises ModelResponseError."""
        mock_client = MagicMock()
        mock_tc = MagicMock()
        mock_tc.id = "call_bad"
        mock_tc.function.name = "read_file"
        mock_tc.function.arguments = "invalid json {{"

        mock_raw_choice = MagicMock()
        mock_raw_choice.message.content = None
        mock_raw_choice.message.tool_calls = [mock_tc]
        mock_raw_choice.finish_reason = "tool_calls"

        mock_raw_response = MagicMock()
        mock_raw_response.choices = [mock_raw_choice]
        mock_raw_response.model = "llama-3.3-70b-versatile"
        mock_raw_response.usage = None

        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        with pytest.raises(ModelResponseError, match="Malformed response from Groq API"):
            provider.generate([Message.user("Hello")])

    def test_generate_malformed_response_type_error_handling(self) -> None:
        """Verify non-indexable/None choices raises ModelResponseError."""
        mock_client = MagicMock()
        mock_raw_response = MagicMock()
        mock_raw_response.choices = None  # None choices causes TypeError on indexing
        mock_client.chat.completions.create.return_value = mock_raw_response

        provider = GroqProvider(client=mock_client)
        with pytest.raises(ModelResponseError, match="Malformed response from Groq API"):
            provider.generate([Message.user("Hello")])

    def test_generate_tool_message_missing_tool_call_id_raises(self) -> None:
        """Verify tool message without tool_call_id raises ModelResponseError."""
        mock_client = MagicMock()
        provider = GroqProvider(client=mock_client)
        bad_tool_msg = Message(role=Role.TOOL, content="result", tool_call_id="")

        with pytest.raises(ModelResponseError, match="Invalid message format"):
            provider.generate([bad_tool_msg])
