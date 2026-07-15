#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/05/04 10:18
@Author  : thezehui@gmail.com
@File    : session_service.py
"""
import logging
from typing import List, Callable, Optional, Type

from app.application.errors.exceptions import NotFoundError, ServerRequestsError
from app.domain.external.file_storage import FileStorage
from app.domain.external.sandbox import Sandbox
from app.domain.external.task import Task
from app.domain.models.file import File
from app.domain.models.session import Session
from app.domain.repositories.uow import IUnitOfWork
from app.interfaces.schemas.session import FileReadResponse, ShellReadResponse

logger = logging.getLogger(__name__)


class SessionService:
    """会话服务"""

    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
            sandbox_cls: Type[Sandbox],
            task_cls: Optional[Type[Task]] = None,
            file_storage: Optional[FileStorage] = None,
    ) -> None:
        """构造函数，完成会话服务初始化"""
        self._uow_factory = uow_factory
        self._uow = uow_factory()
        self._sandbox_cls = sandbox_cls
        self._task_cls = task_cls
        self._file_storage = file_storage

    async def create_session(self) -> Session:
        """创建一个空白的新任务会话"""
        logger.info(f"创建一个空白新任务会话")
        session = Session(title="新对话")
        async with self._uow:
            await self._uow.session.save(session)
        logger.info(f"成功创建一个新任务会话: {session.id}")
        return session

    async def get_all_sessions(self) -> List[Session]:
        """获取项目所有任务会话列表"""
        async with self._uow:
            return await self._uow.session.get_all()

    async def clear_unread_message_count(self, session_id: str) -> None:
        """清空指定会话未读消息数"""
        logger.info(f"清除会话[{session_id}]未读消息数")
        async with self._uow:
            await self._uow.session.update_unread_message_count(session_id, 0)

    async def delete_session(self, session_id: str) -> None:
        """根据传递的会话id删除任务会话"""
        # 1.检查会话是否存在，并找出仅被当前会话引用的文件。
        logger.info(f"正在删除会话, 会话id: {session_id}")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id)
            sessions = await self._uow.session.get_all() if session else []
        if not session:
            logger.error(f"会话[{session_id}]不存在, 删除失败")
            raise NotFoundError(f"会话[{session_id}]不存在, 删除失败")

        other_file_ids = {
            file.id
            for other_session in sessions
            if other_session.id != session_id
            for file in other_session.files
        }
        owned_file_ids = {
            file.id
            for file in session.files
            if file.id and file.id not in other_file_ids
        }

        # 2.先停止后台任务，防止它在删除过程中继续写会话或使用沙箱。
        cleanup_errors: List[str] = []
        if self._task_cls and session.task_id:
            task = self._task_cls.get(session.task_id)
            if task:
                try:
                    await task.dispose()
                except Exception as exc:
                    logger.exception(f"会话[{session_id}]任务资源清理失败")
                    cleanup_errors.append(f"任务: {exc}")

        # 3.销毁会话拥有的动态沙箱；静态直连沙箱的destroy()只关闭客户端。
        if session.sandbox_id:
            try:
                sandbox = await self._sandbox_cls.get(session.sandbox_id)
                if sandbox and not await sandbox.destroy():
                    raise RuntimeError("沙箱返回销毁失败")
            except Exception as exc:
                logger.exception(f"会话[{session_id}]沙箱资源清理失败")
                cleanup_errors.append(f"沙箱: {exc}")

        # 4.清理没有被其他会话引用的持久化文件。删除操作幂等，失败后可重试。
        if self._file_storage:
            for file_id in owned_file_ids:
                try:
                    await self._file_storage.delete_file(file_id)
                except Exception as exc:
                    logger.exception(f"会话[{session_id}]文件[{file_id}]清理失败")
                    cleanup_errors.append(f"文件[{file_id}]: {exc}")

        if cleanup_errors:
            raise ServerRequestsError(
                f"会话[{session_id}]资源清理失败，数据库记录已保留，可重试删除: "
                + "; ".join(cleanup_errors)
            )

        # 5.外部资源清理成功后再删数据库记录，避免丢失失败重试所需的资源标识。
        async with self._uow:
            await self._uow.session.delete_by_id(session_id)
        logger.info(f"删除会话[{session_id}]成功")

    async def get_session(self, session_id: str) -> Session:
        """获取指定会话详情信息"""
        async with self._uow:
            return await self._uow.session.get_by_id(session_id)

    async def get_session_files(self, session_id: str) -> List[File]:
        """根据传递的会话id获取指定会话的文件列表信息"""
        logger.info(f"获取指定会话[{session_id}]下的文件列表信息")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"当前会话不存在[{session_id}], 请核实后重试")
        return session.files

    async def read_file(self, session_id: str, filepath: str) -> FileReadResponse:
        """根据传递的信息查看会话中指定文件的内容"""
        # 1.检查会话是否存在
        logger.info(f"获取会话[{session_id}]中的文件内容, 文件路径: {filepath}")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"当前会话不存在[{session_id}], 请核实后重试")

        # 2.根据沙箱id获取沙箱并判断是否存在
        if not session.sandbox_id:
            raise NotFoundError("当前会话无沙箱环境")
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise NotFoundError("当前会话沙箱不存在或已销毁")

        # 3.调用沙箱读取文件内容
        result = await sandbox.read_file(filepath)
        if result.success:
            return FileReadResponse(**result.data)

        raise ServerRequestsError(result.message)

    async def read_shell_output(self, session_id: str, shell_session_id: str) -> ShellReadResponse:
        """根据传递的任务会话id+Shell会话id获取Shell执行结果"""
        # 1.检查会话是否存在
        logger.info(f"获取会话[{session_id}]中的Shell内容输出, Shell标识符: {shell_session_id}")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"当前会话不存在[{session_id}], 请核实后重试")

        # 2.根据沙箱id获取沙箱并判断是否存在
        if not session.sandbox_id:
            raise NotFoundError("当前会话无沙箱环境")
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise NotFoundError("当前会话沙箱不存在或已销毁")

        # 3.调用沙箱查看shell内容
        result = await sandbox.read_shell_output(session_id=shell_session_id, console=True)
        if result.success:
            return ShellReadResponse(**result.data)

        raise ServerRequestsError(result.message)

    async def get_vnc_url(self, session_id: str) -> str:
        """获取指定会话的vnc链接"""
        # 1.检查会话是否存在
        logger.info(f"获取会话[{session_id}]的VNC链接")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"当前会话不存在[{session_id}], 请核实后重试")

        # 2.根据沙箱id获取沙箱并判断是否存在
        if not session.sandbox_id:
            raise NotFoundError("当前会话无沙箱环境")
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise NotFoundError("当前会话沙箱不存在或已销毁")

        return sandbox.vnc_url
