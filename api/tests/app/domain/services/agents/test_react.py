import pytest

from app.domain.models.app_config import AgentConfig
from app.domain.models.event import ErrorEvent, StepEvent, StepEventStatus
from app.domain.models.message import Message
from app.domain.models.plan import ExecutionStatus, Plan, Step
from app.domain.services.agents.react import ReActAgent


@pytest.mark.anyio
async def test_error_event_leaves_step_failed_after_execute_step_finishes() -> None:
    agent = ReActAgent(
        uow_factory=object,
        session_id="session-1",
        agent_config=AgentConfig(),
        llm=object(),
        json_parser=object(),
        tools=[],
    )

    async def invoke_with_error(_query: str):
        yield ErrorEvent(error="tool execution failed")

    agent.invoke = invoke_with_error
    step = Step(description="run a failing action")
    plan = Plan(language="en", steps=[step])

    events = [
        event
        async for event in agent.execute_step(
            plan=plan,
            step=step,
            message=Message(message="start"),
        )
    ]

    assert step.status == ExecutionStatus.FAILED
    assert step.error == "tool execution failed"
    assert any(
        isinstance(event, StepEvent) and event.status == StepEventStatus.FAILED
        for event in events
    )
    assert any(isinstance(event, ErrorEvent) for event in events)
