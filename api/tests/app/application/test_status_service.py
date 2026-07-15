import pytest

from app.application.services.status_service import StatusService
from app.domain.models.health_status import HealthStatus


class HealthyChecker:
    async def check(self) -> HealthStatus:
        return HealthStatus(service="redis", status="ok", details="pong")


class BrokenChecker:
    async def check(self) -> HealthStatus:
        raise RuntimeError("offline")


@pytest.mark.anyio
async def test_status_service_isolates_checker_failures() -> None:
    result = await StatusService([HealthyChecker(), BrokenChecker()]).check_all()

    assert result[0].status == "ok"
    assert result[1].status == "error"
    assert "offline" in result[1].details
