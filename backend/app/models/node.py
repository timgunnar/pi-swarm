"""Pi 推理节点数据模型."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import TEXT as SQLiteText
from app.models.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(
        SQLiteText, primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending | online | offline | draining
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, default=0.0)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    labels: Mapped[str] = mapped_column(String(500), default="{}")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
