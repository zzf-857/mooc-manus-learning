import inspect

import pytest

from app.domain.models.app_config import AgentConfig
from app.domain.models.search import SearchResultItem, SearchResults
from app.domain.models.tool_result import ToolResult
from app.domain.services.flows.planner_react import PlannerReActFlow
from app.domain.services.tools.base import BaseTool
from app.domain.services.tools.search import SearchTool
from app.domain.services.tools.shell import ShellTool


class SearchEngineStub:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    async def invoke(self, query: str, date_range: str | None = None) -> ToolResult[SearchResults]:
        self.calls.append((query, date_range))
        items = [
            SearchResultItem(
                url=f"https://example.com/{index}",
                title=f"result-{index}",
                snippet=f"snippet-{index}",
            )
            for index in range(5)
        ]
        return ToolResult(
            data=SearchResults(
                query=query,
                date_range=date_range,
                total_results=125,
                results=items,
            )
        )


@pytest.mark.anyio
async def test_unknown_tool_returns_failed_tool_result() -> None:
    result = await BaseTool().invoke("missing_function", unexpected="ignored")

    assert isinstance(result, ToolResult)
    assert result.success is False
    assert result.data is None
    assert "missing_function" in result.message


def test_shell_write_input_press_enter_annotation_matches_boolean_schema() -> None:
    annotation = inspect.signature(ShellTool.shell_write_input).parameters["press_enter"].annotation

    assert annotation is bool


@pytest.mark.anyio
async def test_search_tool_applies_agent_result_limit_without_rewriting_global_total() -> None:
    agent_config = AgentConfig(max_search_results=2)
    search_engine = SearchEngineStub()
    tool = SearchTool(
        search_engine=search_engine,
        max_search_results=agent_config.max_search_results,
    )

    result = await tool.search_web("agent frameworks", "past_week")

    assert result.success is True
    assert result.data is not None
    assert [item.title for item in result.data.results] == ["result-0", "result-1"]
    assert result.data.total_results == 125
    assert search_engine.calls == [("agent frameworks", "past_week")]


def test_planner_react_flow_wires_agent_search_limit_into_search_tool() -> None:
    agent_config = AgentConfig(max_search_results=3)
    search_engine = SearchEngineStub()
    flow = PlannerReActFlow(
        uow_factory=object,
        llm=object(),
        agent_config=agent_config,
        session_id="session-1",
        json_parser=object(),
        browser=object(),
        sandbox=object(),
        search_engine=search_engine,
        mcp_tool=BaseTool(),
        a2a_tool=BaseTool(),
    )

    search_tool = next(tool for tool in flow.planner._tools if isinstance(tool, SearchTool))

    assert search_tool.max_search_results == agent_config.max_search_results
