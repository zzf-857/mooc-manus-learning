from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.application.services.status_service import StatusService
from app.domain.models.health_status import HealthStatus
from app.interfaces.service_dependencies import get_status_service
from app.main import app


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


class HealthyChecker:
    async def check(self) -> HealthStatus:
        return HealthStatus(service="test", status="ok", details="isolated unit test")


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Create a fast unit-test client without starting Postgres/Redis/COS."""
    app.dependency_overrides[get_status_service] = lambda: StatusService([HealthyChecker()])
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides.clear()
