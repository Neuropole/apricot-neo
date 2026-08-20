"""Agent runtime execution loop."""

from __future__ import annotations

from apricot.agent.state import (
    AgentResult,
    AgentState,
    AgentStatus,
    StepRecord,
    ToolExecutionRecord,
)
from apricot.models.base import BaseProvider, Message, ModelError
from apricot.tools.base import ToolRegistry


class Agent:
    """Synchronous tool-calling agent runtime."""

    def __init__(
        self,
        provider: BaseProvider,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 10,
        model: str | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize the Agent.

        Args:
            provider: Concrete BaseProvider instance for LLM inference.
            tools: Optional ToolRegistry containing accessible tools.
            system_prompt: Optional initial system instructions.
            max_iterations: Maximum allowed model -> tool -> model iterations.
            model: Optional model identifier override.
            temperature: Optional sampling temperature.
        """
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.model = model
        self.temperature = temperature

    def run(self, task: str, state: AgentState | None = None) -> AgentResult:
        """Execute the agent on a task or resume from an existing state.

        Args:
            task: Task description or prompt for the agent.
            state: Optional existing AgentState to resume.

        Returns:
            AgentResult containing status, final output, and audit state.
        """
        if state is None:
            messages: list[Message] = []
            if self.system_prompt:
                messages.append(Message.system(self.system_prompt))
            messages.append(Message.user(task))
            state = AgentState(
                task=task,
                messages=messages,
                status=AgentStatus.RUNNING,
            )
        else:
            state.status = AgentStatus.RUNNING
            state.error = None

        while state.current_step < self.max_iterations:
            state.current_step += 1
            tool_defs = self.tools.get_definitions() if self.tools else None

            try:
                response = self.provider.generate(
                    messages=state.messages,
                    tools=tool_defs if tool_defs else None,
                    model=self.model,
                    temperature=self.temperature,
                )
            except ModelError as exc:
                state.status = AgentStatus.FAILED
                state.error = str(exc)
                return AgentResult(
                    success=False,
                    status=AgentStatus.FAILED,
                    response=None,
                    steps_count=state.current_step,
                    state=state,
                    error=str(exc),
                )
            except Exception as exc:
                state.status = AgentStatus.FAILED
                err = f"Unexpected error during generation: {exc}"
                state.error = err
                return AgentResult(
                    success=False,
                    status=AgentStatus.FAILED,
                    response=None,
                    steps_count=state.current_step,
                    state=state,
                    error=err,
                )

            state.messages.append(response.to_message())

            if not response.has_tool_calls:
                state.status = AgentStatus.COMPLETED
                step_record = StepRecord(
                    step_number=state.current_step,
                    model_response=response,
                    tool_executions=[],
                )
                state.steps.append(step_record)
                return AgentResult(
                    success=True,
                    status=AgentStatus.COMPLETED,
                    response=response.content,
                    steps_count=state.current_step,
                    state=state,
                )

            tool_executions: list[ToolExecutionRecord] = []
            for tc in response.tool_calls:
                result = self.tools.execute(name=tc.name, arguments=tc.arguments)
                tool_executions.append(
                    ToolExecutionRecord(
                        call_id=tc.id,
                        tool_name=tc.name,
                        arguments=tc.arguments,
                        result=result,
                    )
                )

                tool_content = result.output if result.success else f"Error: {result.error}"
                state.messages.append(
                    Message.tool_result(
                        tool_call_id=tc.id,
                        content=tool_content,
                        name=tc.name,
                    )
                )

            step_record = StepRecord(
                step_number=state.current_step,
                model_response=response,
                tool_executions=tool_executions,
            )
            state.steps.append(step_record)

        state.status = AgentStatus.MAX_ITERATIONS
        err_msg = f"Reached maximum iteration limit of {self.max_iterations}"
        state.error = err_msg
        return AgentResult(
            success=False,
            status=AgentStatus.MAX_ITERATIONS,
            response=None,
            steps_count=state.current_step,
            state=state,
            error=err_msg,
        )
