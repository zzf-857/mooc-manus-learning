import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Callable, Tuple

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.domain.external.file_storage import FileStorage
from app.domain.models.file import File
from app.domain.repositories.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorage):
    """Store uploaded files on a local volume while metadata stays in Postgres."""

    def __init__(
        self,
        base_path: str,
        uow_factory: Callable[[], IUnitOfWork],
    ) -> None:
        self._base_path = Path(base_path).expanduser().resolve()
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._uow_factory = uow_factory

    def _resolve_key(self, key: str) -> Path:
        path = (self._base_path / key).resolve()
        if not path.is_relative_to(self._base_path):
            raise ValueError("非法文件路径")
        return path

    async def upload_file(self, upload_file: UploadFile) -> File:
        filename = Path(upload_file.filename or "upload").name
        extension = Path(filename).suffix
        file_id = str(uuid.uuid4())
        date_path = datetime.now().strftime("%Y/%m/%d")
        key = f"{date_path}/{file_id}{extension}"
        destination = self._resolve_key(key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        await upload_file.seek(0)

        def copy_to_disk() -> int:
            with destination.open("wb") as target:
                shutil.copyfileobj(upload_file.file, target)
            return destination.stat().st_size

        size = await run_in_threadpool(copy_to_disk)
        file = File(
            id=file_id,
            filename=filename,
            key=key,
            extension=extension,
            mime_type=upload_file.content_type or "application/octet-stream",
            size=size,
        )

        try:
            async with self._uow_factory() as uow:
                await uow.file.save(file)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        logger.info("本地文件上传成功: %s (ID: %s)", filename, file_id)
        return file

    async def download_file(self, file_id: str) -> Tuple[BinaryIO, File]:
        async with self._uow_factory() as uow:
            file = await uow.file.get_by_id(file_id)
        if not file:
            raise ValueError(f"该文件不存在, 文件id: {file_id}")

        path = self._resolve_key(file.key)
        if not path.is_file():
            raise FileNotFoundError(f"文件元数据存在，但本地文件缺失: {file_id}")

        return path.open("rb"), file

    async def delete_file(self, file_id: str) -> None:
        """删除本地文件及其数据库元数据；重复调用是安全的。"""
        async with self._uow_factory() as uow:
            file = await uow.file.get_by_id(file_id)
        if not file:
            return

        path = self._resolve_key(file.key)
        await run_in_threadpool(lambda: path.unlink(missing_ok=True))

        async with self._uow_factory() as uow:
            await uow.file.delete_by_id(file_id)

        logger.info("本地文件删除成功: %s (ID: %s)", file.filename, file_id)
