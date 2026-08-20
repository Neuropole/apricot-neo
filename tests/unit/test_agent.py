"""Unit tests for the Agent runtime loop and execution state."""

from typing import Any
from unittest.mock import MagicMock

from apricot.agent.runtime import Agent
from apricot.agent.state import AgentState, AgentStatus
from apricot.models.base import (
    BaseProvider,
    Message,
    ModelAPIError,
    ModelResponse,
    Role,
    ToolCall,
    ToolDefinition,
)
from apricot.tools.base import BaseTool, FunctionTool, ToolRegistry, ToolResult


class MockProvider(BaseProvider):
    """Mock provider with programmed sequence of responses."""

    def __init__(self, responses: list[ModelResponse]) -> None:
        self.responses = list(responses)
        self.call_count = 0
        self.history: list[dict[str, Any]] = []

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ModelResponse:
        self.call_count += 1
        self.history.append(
            {
                "messages": list(messages),
                "tools": list(tools) if tools else None,
                "model": model,
                "temperature": temperature,
            }
        )
        if not self.responses:
            raise RuntimeError("MockProvider exhausted all pre-configured responses")
        return self.responses.pop(0)


class CalculatorTool(BaseTool):
    """Simple calculator tool for agent testing."""

    @property
    def name(self) -> str:
        return "calc"

    @property
    def description(self) -> str:
        return "Perform basic math operations"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "op": {"type": "string"},
                "x": {"type": "number"},
                "y": {"type": "number"},
            },
            "required": ["op", "x", "y"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        op = kwargs.get("op")
        x = float(kwargs.get("x", 0))
        y = float(kwargs.get("y", 0))

        if op == "add":
            return ToolResult.ok(str(x + y))
        if op == "div":
            if y == 0:
                return ToolResult.failure("Division by zero")
            return ToolResult.ok(str(x / y))
        return ToolResult.failure(f"Unknown operation '{op}'")


class TestAgentRuntime:
    """Tests for the Agent runtime loop."""

    def test_direct_response_without_tools(self) -> None:
        """Test agent when the model directly answers without invoking any tools."""
        provider = MockProvider([ModelResponse(content="The answer is 42.")])
        agent = Agent(provider=provider, system_prompt="You are a helpful assistant.")

        result = agent.run("What is the meaning of life?")

        assert result.success is True
        assert result.status == AgentStatus.COMPLETED
        assert result.response == "The answer is 42."
        assert result.steps_count == 1
        assert len(result.state.steps) == 1
        assert len(result.state.messages) == 3  # system + user + assistant

        # Verify message roles
        assert result.state.messages[0].role == Role.SYSTEM
        assert result.state.messages[1].role == Role.USER
        assert result.state.messages[2].role == Role.ASSISTANT
        assert result.state.messages[2].content == "The answer is 42."

    def test_single_tool_call_and_completion(self) -> None:
        """Test a model -> tool -> model -> answer interaction."""
        tool_call = ToolCall(
            id="call_1",
            name="calc",
            arguments={"op": "add", "x": 10, "y": 32},
        )
        provider = MockProvider(
            [
                ModelResponse(content=None, tool_calls=[tool_call]),
                ModelResponse(content="10 + 32 is 42."),
            ]
        )

        registry = ToolRegistry()
        registry.register(CalculatorTool())

        agent = Agent(provider=provider, tools=registry)
        result = agent.run("Calculate 10 + 32")

        assert result.success is True
        assert result.status == AgentStatus.COMPLETED
        assert result.response == "10 + 32 is 42."
        assert result.steps_count == 2
        assert len(result.state.steps) == 2

        # Verify step 1 tool executions
        step1 = result.state.steps[0]
        assert len(step1.tool_executions) == 1
        assert step1.tool_executions[0].tool_name == "calc"
        assert step1.tool_executions[0].result.success is True
        assert step1.tool_executions[0].result.output == "42.0"

        # Verify message sequence: user -> assistant(tool_call) -> tool(result) -> assistant(answer)
        msgs = result.state.messages
        assert len(msgs) == 4
        assert msgs[0].role == Role.USER
        assert msgs[1].role == Role.ASSISTANT
        assert msgs[1].tool_calls == [tool_call]
        assert msgs[2].role == Role.TOOL
        assert msgs[2].tool_call_id == "call_1"
        assert msgs[2].content == "42.0"
        assert msgs[3].role == Role.ASSISTANT
        assert msgs[3].content == "10 + 32 is 42."

    def test_multiple_tool_calls_in_single_iteration(self) -> None:
        """Test handling multiple tool calls issued in a single response."""
        tc1 = ToolCall(id="c1", name="calc", arguments={"op": "add", "x": 1, "y": 2})
        tc2 = ToolCall(id="c2", name="calc", arguments={"op": "add", "x": 3, "y": 4})

        provider = MockProvider(
            [
                ModelResponse(content=None, tool_calls=[tc1, tc2]),
                ModelResponse(content="Results are 3 and 7."),
            ]
        )

        registry = ToolRegistry()
        registry.register(CalculatorTool())

        agent = Agent(provider=provider, tools=registry)
        result = agent.run("Calculate 1+2 and 3+4")

        assert result.success is True
        assert result.steps_count == 2

        # Step 1 should record both executions
        step1 = result.state.steps[0]
        assert len(step1.tool_executions) == 2
        assert step1.tool_executions[0].result.output == "3.0"
        assert step1.tool_executions[1].result.output == "7.0"

        # Message history should have user -> assistant(2 calls) -> tool1 -> tool2 -> assistant
        assert len(result.state.messages) == 5
        assert result.state.messages[2].tool_call_id == "c1"
        assert result.state.messages[3].tool_call_id == "c2"

    def test_multiple_iterations_across_steps(self) -> None:
        """Test multi-step chaining across 3 iterations."""
        tc1 = ToolCall(id="c1", name="calc", arguments={"op": "add", "x": 10, "y": 10})
        tc2 = ToolCall(id="c2", name="calc", arguments={"op": "add", "x": 20, "y": 5})

        provider = MockProvider(
            [
                ModelResponse(content=None, tool_calls=[tc1]),
                ModelResponse(content=None, tool_calls=[tc2]),
                ModelResponse(content="Final accumulated value is 25."),
            ]
        )

        registry = ToolRegistry()
        registry.register(CalculatorTool())

        agent = Agent(provider=provider, tools=registry, max_iterations=5)
        result = agent.run("Add numbers iteratively")

        assert result.success is True
        assert result.steps_count == 3
        assert result.response == "Final accumulated value is 25."
        assert len(result.state.steps) == 3

    def test_unknown_tool_handling(self) -> None:
        """Test that invoking an unknown tool returns an error message and does not crash."""
        tc_unknown = ToolCall(id="c_err", name="nonexistent_tool", arguments={})

        provider = MockProvider(
            [
                ModelResponse(content=None, tool_calls=[tc_unknown]),
                ModelResponse(content="Sorry, I tried to use an unavailable tool."),
            ]
        )

        agent = Agent(provider=provider, tools=ToolRegistry())
        result = agent.run("Do something impossible")

        assert result.success is True
        assert result.status == AgentStatus.COMPLETED
        assert result.response == "Sorry, I tried to use an unavailable tool."

        # Verify tool error message passed back to model
        tool_msg = result.state.messages[2]
        assert tool_msg.role == Role.TOOL
        assert "Error: Unknown tool: 'nonexistent_tool'" in (tool_msg.content or "")

    def test_tool_failure_handling(self) -> None:
        """Test that a failing tool returns failure content to model."""
        tc_fail = ToolCall(id="c_fail", name="calc", arguments={"op": "div", "x": 10, "y": 0})

        provider = MockProvider(
            [
                ModelResponse(content=None, tool_calls=[tc_fail]),
                ModelResponse(content="Cannot divide by zero."),
            ]
        )

        registry = ToolRegistry()
        registry.register(CalculatorTool())

        agent = Agent(provider=provider, tools=registry)
        result = agent.run("Divide 10 by 0")

        assert result.success is True
        assert result.response == "Cannot divide by zero."

        # Verify the tool result contained the error
        step1 = result.state.steps[0]
        assert step1.tool_executions[0].result.success is False
        assert step1.tool_executions[0].result.error == "Division by zero"

    def test_max_iteration_limit_enforced(self) -> None:
        """Test that reaching maximum iterations terminates with MAX_ITERATIONS status."""
        # Infinite tool calling loop
        infinite_tc = ToolCall(id="c_loop", name="ping", arguments={})
        responses = [ModelResponse(content=None, tool_calls=[infinite_tc]) for _ in range(5)]
        provider = MockProvider(responses)

        registry = ToolRegistry()
        registry.register(
            FunctionTool(
                name="ping",
                description="Ping",
                parameters={"type": "object"},
                fn=lambda: "pong",
            )
        )

        agent = Agent(provider=provider, tools=registry, max_iterations=3)
        result = agent.run("Loop forever")

        assert result.success is False
        assert result.status == AgentStatus.MAX_ITERATIONS
        assert result.steps_count == 3
        assert "Reached maximum iteration limit of 3" in (result.error or "")

    def test_provider_failure_handling(self) -> None:
        """Test graceful failure handling when LLM provider throws ModelAPIError."""
        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.generate.side_effect = ModelAPIError("Upstream API is down")

        agent = Agent(provider=mock_provider)
        result = agent.run("Test failure")

        assert result.success is False
        assert result.status == AgentStatus.FAILED
        assert "Upstream API is down" in (result.error or "")
        assert result.state.status == AgentStatus.FAILED

    def test_resuming_existing_state(self) -> None:
        """Test resuming an agent run from an existing state."""
        existing_state = AgentState(
            task="Original task",
            messages=[Message.user("Previous context")],
            current_step=1,
        )

        provider = MockProvider([ModelResponse(content="Resumed and finished.")])
        agent = Agent(provider=provider, max_iterations=5)

        result = agent.run("Continue", state=existing_state)

        assert result.success is True
        assert result.status == AgentStatus.COMPLETED
        assert result.steps_count == 2
        assert result.response == "Resumed and finished."
