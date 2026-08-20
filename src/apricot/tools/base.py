"""Base provider-independent tool abstractions and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from apricot.models.base import ToolDefinition


@dataclass(frozen=True)
class ToolResult:
    """Normalized result of a tool execution."""

    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, output: str, metadata: dict[str, Any] | None = None) -> ToolResult:
        """Construct a successful tool result."""
        return cls(success=True, output=output, metadata=metadata or {})

    @classmethod
    def failure(
        cls, error: str, output: str = "", metadata: dict[str, Any] | None = None
    ) -> ToolResult:
        """Construct a failed tool result."""
        return cls(success=False, output=output, error=error, metadata=metadata or {})


class BaseTool(ABC):
    """Abstract base class for all agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human/LLM readable description of what the tool does."""

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema dictionary describing the expected input parameters."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with provided arguments and return a ToolResult.

        Args:
            **kwargs: Keyword arguments matching the parameters schema.

        Returns:
            Normalized ToolResult.
        """

    def to_definition(self) -> ToolDefinition:
        """Convert tool specification to universal ToolDefinition."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )


class FunctionTool(BaseTool):
    """Convenience tool wrapper around a Python callable."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        fn: Callable[..., Any],
    ) -> None:
        self._name = name
        self._description = description
        self._parameters = parameters
        self._fn = fn

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> dict[str, Any]:
        return self._parameters

    def execute(self, **kwargs: Any) -> ToolResult:
        try:
            res = self._fn(**kwargs)
            if isinstance(res, ToolResult):
                return res
            return ToolResult.ok(str(res))
        except Exception as exc:
            return ToolResult.failure(error=f"Error executing '{self.name}': {exc}")


class ToolRegistryError(Exception):
    """Exception raised for tool registry errors (e.g. duplicate names)."""


class ToolRegistry:
    """Registry managing available tools and safe execution dispatch."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool, overwrite: bool = False) -> None:
        """Register a tool in the registry.

        Args:
            tool: BaseTool instance to register.
            overwrite: If True, allows replacing an existing tool with the same name.

        Raises:
            ToolRegistryError: If a tool with the same name is already registered
                and overwrite is False.
        """
        name = tool.name
        if not overwrite and name in self._tools:
            raise ToolRegistryError(
                f"Tool with name '{name}' is already registered in this ToolRegistry."
            )
        self._tools[name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """Return a list of all registered tools."""
        return list(self._tools.values())

    def get_definitions(self) -> list[ToolDefinition]:
        """Return universal ToolDefinitions for all registered tools."""
        return [tool.to_definition() for tool in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        """Safely execute a registered tool by name with arguments.

        Args:
            name: Tool name.
            arguments: Dictionary of arguments.

        Returns:
            Normalized ToolResult (failure result if tool is unknown or raises).
        """
        tool = self.get(name)
        if tool is None:
            return ToolResult.failure(error=f"Unknown tool: '{name}'")

        try:
            return tool.execute(**arguments)
        except Exception as exc:
            return ToolResult.failure(error=f"Tool execution failed for '{name}': {exc}")
