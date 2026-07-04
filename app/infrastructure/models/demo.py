import uuid
from pydoc import text

from datetime import datetime

from .base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import (
    UUID,
    String,
    Text,
    DateTime,
    PrimaryKeyConstraint,
    text
)


class Demo(Base):
    """Demo 模型，用于演示alembic数据迁移"""
    __tablename__ = "demos"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_demos_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=False,
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )  # demo id
    name: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))#名字
    avatar: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))#头像
    email: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))#邮箱
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))  # 描述
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),  # 获取当前的时间戳
        onupdate=datetime.now
    )  # 更新时间

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),  # 获取当前的时间戳
    )  # 创建时间
