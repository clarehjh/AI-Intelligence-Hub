'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 19:50:56
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 14:05:52
'''


from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    title: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    url: Mapped[str] = mapped_column(
        String(1000), nullable=False, unique=True, index=True
    )

    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    content: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    content_type: Mapped[str] = mapped_column(
        String(50), default="article"
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )