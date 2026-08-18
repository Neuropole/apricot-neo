"""Agent state models and execution records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apricot.models.base import Message, ModelResponse
from apricot.tools.base import ToolResult


class AgentStatus(str, Enum):
    """Lifecycle and execution status of the agent."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    MAX_ITERATIONS = "max_iterations"
    FAILED = "failed"


@dataclass(frozen=True)
class ToolExecutionRecord:
    """Audit record for a single tool call execution."""

    call_id: str
    tool_name: str
    arguments: dict[str, Any]
    result: ToolResult


@dataclass
class StepRecord:
    """Record of a single iteration step within the agent loop."""

    step_number: int
    model_response: ModelResponse
    tool_executions: list[ToolExecutionRecord] = field(default_factory=list)


@dataclass
class AgentState:
    """Durable state tracking of an agent run."""

    task: str
    messages: list[Message] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_step: int = 0
    steps: list[StepRecord] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    """Final result and summary of an agent execution."""

    success: bool
    status: AgentStatus
    response: str | None
    steps_count: int
    state: AgentState
    error: str | None = None
