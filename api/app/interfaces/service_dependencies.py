#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/17 10:54
@Author  : thezehui@gmail.com
@File    : dependencies.py
"""
import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_service import AgentService
from app.application.services.app_config_service import AppConfigService
from app.application.services.file_service import FileService
from app.application.services.session_service import SessionService
from app.application.services.status_service import StatusService
from app.infrastructure.external.file_storage.cos_file_storage import CosFileStorage
from app.infrastructure.external.file_storage.local_file_storage import LocalFileStorage
from app.infrastructure.external.health_checker.postgres_health_checker import PostgresHealthChecker
from app.infrastructure.external.health_checker.redis_health_checker import RedisHealthChecker
from app.infrastructure.external.json_parser.repair_json_parser import RepairJSONParser
from app.infrastructure.external.llm.openai_llm import OpenAILLM
from app.infrastructure.external.sandbox.docker_sandbox import DockerSandbox
from app.infrastructure.external.search.bing_search import BingSearchEngine
from app.infrastructure.external.task.redis_stream_task import RedisStreamTask
from app.infrastructure.repositories.file_app_config_repository import FileAppConfigRepository
from app.infrastructure.storage.cos import Cos, get_cos
from app.infrastructure.storage.postgres import get_db_session, get_uow
from app.infrastructure.storage.redis import RedisClient, get_redis
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_file_storage(cos: Cos):
    """Select the configured storage adapter without leaking backend details upward."""
    backend = settings.file_storage_backend.strip().lower()
    if backend == "local":
        return LocalFileStorage(
            base_path=settings.local_storage_path,
            uow_factory=get_uow,
        )
    if backend == "cos":
        if not settings.cos_bucket:
            raise RuntimeError("FILE_STORAGE_BACKEND=cos 时必须配置 COS_BUCKET")
        return CosFileStorage(
            bucket=settings.cos_bucket,
            cos=cos,
            uow_factory=get_uow,
        )
    raise RuntimeError(f"不支持的 FILE_STORAGE_BACKEND: {settings.file_storage_backend}")


def get_app_config_service() -> AppConfigService:
    """获取应用配置服务"""
    # 1.获取数据仓库并打印日志
    logger.info("加载获取AppConfigService")
    file_app_config_repository = FileAppConfigRepository(settings.app_config_filepath)

    # 2.实例化AppConfigService
    return AppConfigService(app_config_repository=file_app_config_repository)


def get_status_service(
        db_session: AsyncSession = Depends(get_db_session),
        redis_client: RedisClient = Depends(get_redis),
) -> StatusService:
    """获取状态服务"""
    # 1.初始化postgres和redis健康检查
    postgres_checker = PostgresHealthChecker(db_session)
    redis_checker = RedisHealthChecker(redis_client)

    # 2.创建服务并返回
    logger.info("加载获取StatusService")
    return StatusService(checkers=[postgres_checker, redis_checker])


def get_file_service(
        cos: Cos = Depends(get_cos)
) -> FileService:
    # 存储实现由配置选择，应用服务只依赖 FileStorage 协议。
    return FileService(
        uow_factory=get_uow,
        file_storage=_get_file_storage(cos),
    )


def get_session_service(
        cos: Cos = Depends(get_cos),
) -> SessionService:
    return SessionService(
        uow_factory=get_uow,
        sandbox_cls=DockerSandbox,
        task_cls=RedisStreamTask,
        file_storage=_get_file_storage(cos),
    )


def get_agent_service(
        cos: Cos = Depends(get_cos),
) -> AgentService:
    # 1.获取应用配置信息(读取配置需要实时获取,所以不配置缓存)
    app_config_repository = FileAppConfigRepository(config_path=settings.app_config_filepath)
    app_config = app_config_repository.load()

    # 2.构建依赖实例
    llm = OpenAILLM(app_config.llm_config)
    file_storage = _get_file_storage(cos)

    # 3.实例Agent服务并返回
    return AgentService(
        uow_factory=get_uow,
        llm=llm,
        agent_config=app_config.agent_config,
        mcp_config=app_config.mcp_config,
        a2a_config=app_config.a2a_config,
        sandbox_cls=DockerSandbox,
        task_cls=RedisStreamTask,
        json_parser=RepairJSONParser(),
        search_engine=BingSearchEngine(),
        file_storage=file_storage,
    )
