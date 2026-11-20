"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 18:13:01
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 18:14:34
"""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class NewsAnalysisRecord(Base):
    __tablename__ = "news_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    news_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("news.id"), unique=True, nullable=False
    )

    result: Mapped[dict] = mapped_column(JSON, nullable=False)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
