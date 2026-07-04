import logging

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus
from app.infrastructure.storage.redis import RedisClient


logger = logging.getLogger(__name__)


class RedisHealthChecker(HealthChecker):
    """redis健康检查器"""

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis_client = redis_client

    async def check(self) -> HealthStatus:
        """执行一段简单的sql，用于判断数据库服务是否正常"""
        try:
            if await self.redis_client.client.ping():
                return HealthStatus(
                    service="redis",
                    status="ok"
                )
            else:
                return HealthStatus(
                    service="redis",
                    status="error",
                    details="Redis服务Ping失败"
                )
        except Exception as e:
            logger.error(f"Redis健康检查失败：{str(e)}")
            return HealthStatus(
                service="redis",
                status="error",
                details=str(e),
            )
