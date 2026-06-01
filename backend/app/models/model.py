"""已部署模型数据模型."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import TEXT as SQLiteText
from app.models.base import Base


class ModelInfo(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(
        SQLiteText, primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag: Mapped[str] = mapped_column(String(50), default="latest")
    size: Mapped[str] = mapped_column(String(50), default="")
    quantization: Mapped[str] = mapped_column(String(20), default="Q4_K_M")
    replicas: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(20), default="deploying"
    )  # deploying | ready | error | unloaded
    engine: Mapped[str] = mapped_column(String(30), default="ollama")
    deployed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
