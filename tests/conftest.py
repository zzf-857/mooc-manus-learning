import pytest

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    创建一个可供所有测试用例使用的  TestClient客户端
    scope="session"  标识这个fixture 在整个测试用例中只会实例一次，这样可以提高效率
    :return: TestClient
    """
    with TestClient(app) as c:
        yield c