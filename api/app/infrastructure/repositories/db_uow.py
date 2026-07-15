#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/05/06 15:44
@Author  : thezehui@gmail.com
@File    : db_uow.py
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.domain.repositories.uow import IUnitOfWork
from .db_file_repository import DBFileRepository
from .db_session_repository import DBSessionRepository

logger = logging.getLogger(__name__)


class DBUnitOfWork(IUnitOfWork):
    """基于Postgres数据库的UoW实例"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """构造函数，完成UoW类初始化"""
        self.session_factory = session_factory
        self.db_session: Optional[AsyncSession] = None

    async def commit(self):
        """提交数据库持久化"""
        await self.db_session.commit()

    async def rollback(self):
        """数据库回退操作"""
        await self.db_session.rollback()

    async def __aenter__(self) -> "DBUnitOfWork":
        """进入UoW操作上下文管理器的逻辑"""
        # 1.为每个上下文开启一个新的会话
        self.db_session = self.session_factory()

        # 2.初始化所有数据库仓库
        self.file = DBFileRepository(db_session=self.db_session)
        self.session = DBSessionRepository(db_session=self.db_session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异常时回滚，正常时提交，并确保事务失败不会被伪装成成功。"""
        if self.db_session is None:
            return False

        if exc_type is not None:
            try:
                await self.rollback()
            except BaseException:
                # 回滚失败必须向上传播；否则连接/事务状态未知，调用方却会误以为
                # 原事务只按预期失败。关闭失败只记录，避免覆盖更关键的回滚异常。
                try:
                    await self.db_session.close()
                except BaseException:
                    logger.exception("UoW回滚失败后，关闭数据库会话也失败")
                finally:
                    self.db_session = None
                raise

            try:
                await self.db_session.close()
            except BaseException:
                # 业务异常已经存在时保留原始异常，避免close错误掩盖根因。
                logger.exception("UoW回滚后关闭数据库会话失败")
            finally:
                self.db_session = None
            return False

        try:
            await self.commit()
        except BaseException:
            # 提交失败是本次工作单元的主错误；尽力关闭会话后原样传播。
            try:
                await self.db_session.close()
            except BaseException:
                logger.exception("UoW提交失败后，关闭数据库会话也失败")
            finally:
                self.db_session = None
            raise

        try:
            await self.db_session.close()
        finally:
            self.db_session = None
        return False
