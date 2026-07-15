from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.models.app_config import (
    A2AConfig,
    A2AServerConfig,
    MCPConfig,
    MCPServerConfig,
    MCPTransport,
)
from app.domain.services.tools import mcp as mcp_module
from app.domain.services.tools.a2a import A2AClientManager, A2ATool
from app.domain.services.tools.mcp import MCPClientManager


def make_http_mcp_server(*, enabled: bool) -> MCPServerConfig:
    return MCPServerConfig(
        transport=MCPTransport.STREAMABLE_HTTP,
        url="https://mcp.example.test",
        enabled=enabled,
    )


@pytest.mark.anyio
async def test_mcp_initialization_skips_disabled_servers() -> None:
    config = MCPConfig(
        mcpServers={
            "enabled": make_http_mcp_server(enabled=True),
            "disabled": make_http_mcp_server(enabled=False),
        }
    )
    manager = MCPClientManager(config)
    manager._connect_mcp_server = AsyncMock()

    await manager._connect_mcp_servers()

    manager._connect_mcp_server.assert_awaited_once_with(
        "enabled",
        config.mcpServers["enabled"],
    )
    assert manager.tools["disabled"] == []


@pytest.mark.anyio
async def test_mcp_invoke_rejects_disabled_server_even_if_a_stale_client_exists() -> None:
    config = MCPConfig(mcpServers={"disabled": make_http_mcp_server(enabled=False)})
    manager = MCPClientManager(config)
    stale_session = SimpleNamespace(call_tool=AsyncMock())
    manager._clients["disabled"] = stale_session

    result = await manager.invoke("mcp_disabled_echo", {"text": "hello"})

    assert result.success is False
    assert "disabled" in result.message
    stale_session.call_tool.assert_not_awaited()


@pytest.mark.anyio
async def test_mcp_stdio_accepts_missing_env_and_inherits_process_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    session = SimpleNamespace(
        initialize=AsyncMock(),
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
    )

    @asynccontextmanager
    async def fake_stdio_client(parameters):
        captured["parameters"] = parameters
        yield object(), object()

    @asynccontextmanager
    async def fake_client_session(*_args):
        yield session

    monkeypatch.setenv("MOOC_MANUS_TEST_ENV", "inherited")
    monkeypatch.setattr(mcp_module, "stdio_client", fake_stdio_client)
    monkeypatch.setattr(
        mcp_module,
        "ClientSession",
        lambda *_args: fake_client_session(),
    )

    manager = MCPClientManager()
    server = MCPServerConfig(
        transport=MCPTransport.STDIO,
        command="fake-mcp-server",
        args=None,
        env=None,
    )
    try:
        await manager._connect_stdio_server("stdio", server)
    finally:
        await manager._exit_stack.aclose()

    parameters = captured["parameters"]
    assert parameters.args == []
    assert parameters.env["MOOC_MANUS_TEST_ENV"] == "inherited"
    session.initialize.assert_awaited_once_with()


class ResponseStub:
    def __init__(self, name: str) -> None:
        self.name = name

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "url": f"https://agents.example.test/{self.name}",
        }


@pytest.mark.anyio
async def test_a2a_manager_skips_disabled_servers_by_default() -> None:
    config = A2AConfig(
        a2a_servers=[
            A2AServerConfig(id="enabled", base_url="https://enabled.example.test", enabled=True),
            A2AServerConfig(id="disabled", base_url="https://disabled.example.test", enabled=False),
        ]
    )
    manager = A2AClientManager(config)
    manager._httpx_client = SimpleNamespace(
        get=AsyncMock(return_value=ResponseStub("enabled"))
    )

    await manager._get_a2a_agent_cards()

    assert set(manager.agent_cards) == {"enabled"}
    assert manager.agent_cards["enabled"]["enabled"] is True
    manager._httpx_client.get.assert_awaited_once_with(
        "https://enabled.example.test/.well-known/agent-card.json"
    )


@pytest.mark.anyio
async def test_a2a_manager_can_include_disabled_cards_for_configuration() -> None:
    config = A2AConfig(
        a2a_servers=[
            A2AServerConfig(id="enabled", base_url="https://enabled.example.test", enabled=True),
            A2AServerConfig(id="disabled", base_url="https://disabled.example.test", enabled=False),
        ]
    )
    manager = A2AClientManager(config, include_disabled=True)
    manager._httpx_client = SimpleNamespace(
        get=AsyncMock(side_effect=[ResponseStub("enabled"), ResponseStub("disabled")])
    )

    await manager._get_a2a_agent_cards()

    assert set(manager.agent_cards) == {"enabled", "disabled"}
    assert manager.agent_cards["disabled"]["enabled"] is False
    assert manager._httpx_client.get.await_count == 2


@pytest.mark.anyio
async def test_a2a_tool_exposes_only_enabled_agents(monkeypatch: pytest.MonkeyPatch) -> None:
    config = A2AConfig(
        a2a_servers=[
            A2AServerConfig(id="enabled", base_url="https://enabled.example.test", enabled=True),
            A2AServerConfig(id="disabled", base_url="https://disabled.example.test", enabled=False),
        ]
    )
    initialized_ids: list[str] = []
    include_disabled_flags: list[bool] = []

    async def fake_initialize(manager: A2AClientManager) -> None:
        initialized_ids.extend(server.id for server in manager._a2a_config.a2a_servers)
        include_disabled_flags.append(manager._include_disabled)
        manager._agent_cards = {
            server.id: {
                "name": server.id,
                "url": server.base_url,
                "enabled": server.enabled,
            }
            for server in manager._a2a_config.a2a_servers
        }
        # A stale card must still be hidden by the public tool response.
        manager._agent_cards["stale-disabled"] = {
            "name": "stale-disabled",
            "url": "https://stale.example.test",
            "enabled": False,
        }
        manager._initialized = True

    monkeypatch.setattr(A2AClientManager, "initialize", fake_initialize)

    tool = A2ATool()
    await tool.initialize(config)
    result = await tool.get_remote_agent_cards()

    assert initialized_ids == ["enabled", "disabled"]
    assert include_disabled_flags == [False]
    assert result.success is True
    assert [card["id"] for card in result.data] == ["enabled"]


@pytest.mark.anyio
async def test_a2a_invoke_rejects_disabled_agent_before_http_request() -> None:
    manager = A2AClientManager()
    manager._agent_cards["disabled"] = {
        "url": "https://agents.example.test/disabled",
        "enabled": False,
    }
    manager._httpx_client = SimpleNamespace(post=AsyncMock())

    result = await manager.invoke("disabled", "do work")

    assert result.success is False
    assert "disabled" in result.message
    manager._httpx_client.post.assert_not_awaited()
