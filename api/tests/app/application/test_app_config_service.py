import pytest

from app.application.services import app_config_service as app_config_service_module
from app.application.services.app_config_service import AppConfigService
from app.domain.models.app_config import (
    A2AConfig,
    A2AServerConfig,
    AgentConfig,
    AppConfig,
    LLMConfig,
    MCPConfig,
)


class AppConfigRepositoryStub:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.saved: list[AppConfig] = []

    def load(self) -> AppConfig:
        return self.config

    def save(self, config: AppConfig) -> None:
        self.saved.append(config)


def make_app_config() -> AppConfig:
    return AppConfig(
        llm_config=LLMConfig(),
        agent_config=AgentConfig(),
        mcp_config=MCPConfig(),
        a2a_config=A2AConfig(
            a2a_servers=[
                A2AServerConfig(id="keep", base_url="https://keep.example.test"),
                A2AServerConfig(id="remove", base_url="https://remove.example.test"),
            ]
        ),
    )


@pytest.mark.anyio
async def test_a2a_mutations_return_a2a_config() -> None:
    app_config = make_app_config()
    repository = AppConfigRepositoryStub(app_config)
    service = AppConfigService(repository)

    enabled_result = await service.set_a2a_server_enabled("keep", False)
    delete_result = await service.delete_a2a_server("remove")

    assert isinstance(enabled_result, A2AConfig)
    assert enabled_result is app_config.a2a_config
    assert enabled_result.a2a_servers[0].enabled is False
    assert isinstance(delete_result, A2AConfig)
    assert delete_result is app_config.a2a_config
    assert [server.id for server in delete_result.a2a_servers] == ["keep"]
    assert repository.saved == [app_config, app_config]


@pytest.mark.anyio
async def test_a2a_configuration_listing_explicitly_includes_disabled_servers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_config = make_app_config()
    app_config.a2a_config.a2a_servers[1].enabled = False
    repository = AppConfigRepositoryStub(app_config)
    include_disabled_values: list[bool] = []

    class A2AManagerStub:
        def __init__(self, _config: A2AConfig, include_disabled: bool = False) -> None:
            include_disabled_values.append(include_disabled)
            self.agent_cards = {
                "keep": {"name": "keep", "enabled": True},
                "remove": {"name": "remove", "enabled": False},
            }

        async def initialize(self) -> None:
            return None

        async def cleanup(self) -> None:
            return None

    monkeypatch.setattr(app_config_service_module, "A2AClientManager", A2AManagerStub)

    result = await AppConfigService(repository).get_a2a_servers()

    assert include_disabled_values == [True]
    assert {item.id: item.enabled for item in result} == {
        "keep": True,
        "remove": False,
    }
