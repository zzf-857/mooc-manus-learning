import logging
from typing import Optional
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine,AsyncSession, async_sessionmaker, create_async_engine
from core.config import get_settings

logger = logging.getLogger(__name__)


class Postgres:
    """Postgres数据库基类，用于完成数据库连接等配置操作"""

    def __init__(self):
        """构造函数，完成postgres数据库引擎、会话工厂的创建"""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self) -> None:
        """初始化postgres连接"""
        # 1. 判断是否已经创建好引擎，如果连上了则中断程序
        if self._engine is not None:
            logger.warning(f"Postgres引擎已初始化，无需重复操作")
            return
        try:
            # 2.创建异步引擎
            logger.info("正在初始化Postgres连接....")
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_uri,
                echo=True if self._settings.env == 'development' else False,
            )

            # 3. 创建会话工厂
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            logger.info("Postgres会话工厂创建成功....")

            # 4.连接Postgres并执行预操作
            async with self._engine.begin() as async_conn:
                await async_conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                logger.info("成功连接Postgres并安装uuid-ossp拓展")
        except Exception as e:
            logger.error(f"连接Postgres失败：{str(e)}")
            raise

    async def shutdown(self) -> None:
        """关闭postgres连接"""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("成功关闭Postgres连接")

        get_postgres.cache_clear()

    @property
    def session_factory(self)-> async_sessionmaker[AsyncSession]:
        """只读属性，返回已初始化的会话工厂"""
        if self._session_factory is None:
            raise RuntimeError("Postgres未初始化，请先调用init函数")
        return self._session_factory


@lru_cache()
def get_postgres() -> Postgres:
    """使用lru_cache实现单例模式，获取postgres实例"""
    return Postgres()


async def get_db_session()-> AsyncSession:
    """FastAPI依赖项，用于在美国和请求中异步获取数据库会话实例，确保会话在正确使用后被关闭"""
    # 1. 获取引擎和会话工厂
    db=get_postgres()
    session_factory= db.session_factory


    # 2. 创建会话上下文，在上下文完成数据提交
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as _:
            await session.rollback()
            raise






