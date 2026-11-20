"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 15:26:34
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:26:48
"""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class CrawlerTask(Base):
    __tablename__ = "crawler_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")

    total: Mapped[int] = mapped_column(Integer, default=0)

    saved: Mapped[int] = mapped_column(Integer, default=0)

    skipped: Mapped[int] = mapped_column(Integer, default=0)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
