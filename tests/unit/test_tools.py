"""Unit tests for the tool abstraction and ToolRegistry."""

from typing import Any

import pytest

from apricot.models.base import ToolDefinition
from apricot.tools.base import (
    BaseTool,
    FunctionTool,
    ToolRegistry,
    ToolRegistryError,
    ToolResult,
)


class DummyEchoTool(BaseTool):
    """Test tool that echoes an input message."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echoes back the input text"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        text = kwargs.get("text", "")
        return ToolResult.ok(f"Echo: {text}", metadata={"length": len(text)})


class FailingTool(BaseTool):
    """Test tool that intentionally raises an exception during execution."""

    @property
    def name(self) -> str:
        return "failing_tool"

    @property
    def description(self) -> str:
        return "A tool that raises an exception"

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self, **kwargs: Any) -> ToolResult:
        raise RuntimeError("Crash inside tool execution")


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_ok_result(self) -> None:
        res = ToolResult.ok("Success output", metadata={"key": "val"})
        assert res.success is True
        assert res.output == "Success output"
        assert res.error is None
        assert res.metadata == {"key": "val"}

    def test_failure_result(self) -> None:
        res = ToolResult.failure("Some error message", output="Partial output")
        assert res.success is False
        assert res.error == "Some error message"
        assert res.output == "Partial output"


class TestBaseToolAndFunctionTool:
    """Tests for BaseTool and FunctionTool wrapper."""

    def test_to_definition(self) -> None:
        tool = DummyEchoTool()
        defn = tool.to_definition()
        assert isinstance(defn, ToolDefinition)
        assert defn.name == "echo"
        assert defn.description == "Echoes back the input text"
        assert "text" in defn.parameters["properties"]

    def test_function_tool_execution(self) -> None:
        def add(a: int, b: int) -> int:
            return a + b

        tool = FunctionTool(
            name="add",
            description="Add two numbers",
            parameters={
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
            fn=add,
        )
        assert tool.name == "add"
        res = tool.execute(a=3, b=5)
        assert res.success is True
        assert res.output == "8"

    def test_function_tool_exception_handling(self) -> None:
        def bad_fn() -> None:
            raise ValueError("Invalid operation")

        tool = FunctionTool(
            name="bad_tool",
            description="Fails",
            parameters={"type": "object"},
            fn=bad_fn,
        )
        res = tool.execute()
        assert res.success is False
        assert "Error executing 'bad_tool': Invalid operation" in (res.error or "")


class TestToolRegistry:
    """Tests for ToolRegistry management and execution dispatch."""

    def test_register_and_get(self) -> None:
        registry = ToolRegistry()
        tool = DummyEchoTool()
        registry.register(tool)

        assert registry.get("echo") == tool
        assert registry.get("nonexistent") is None
        assert registry.list_tools() == [tool]

        definitions = registry.get_definitions()
        assert len(definitions) == 1
        assert definitions[0].name == "echo"

    def test_duplicate_registration_protection(self) -> None:
        registry = ToolRegistry()
        tool1 = DummyEchoTool()
        tool2 = DummyEchoTool()

        registry.register(tool1)
        with pytest.raises(ToolRegistryError, match="already registered"):
            registry.register(tool2, overwrite=False)

        # Overwrite should succeed
        registry.register(tool2, overwrite=True)
        assert registry.get("echo") == tool2

    def test_execute_registered_tool(self) -> None:
        registry = ToolRegistry()
        registry.register(DummyEchoTool())

        res = registry.execute("echo", {"text": "hello world"})
        assert res.success is True
        assert res.output == "Echo: hello world"

    def test_execute_unknown_tool(self) -> None:
        registry = ToolRegistry()
        res = registry.execute("unknown_tool", {})
        assert res.success is False
        assert res.error == "Unknown tool: 'unknown_tool'"

    def test_execute_tool_with_uncaught_exception(self) -> None:
        registry = ToolRegistry()
        registry.register(FailingTool())

        res = registry.execute("failing_tool", {})
        assert res.success is False
        assert "Tool execution failed for 'failing_tool': Crash inside tool execution" in (
            res.error or ""
        )
