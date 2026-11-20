
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class NewsSource(Base):
    """新闻来源模型"""

    __tablename__ = "news_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    url: Mapped[str] = mapped_column(
        String(1000), nullable=False, unique=True, index=True
    )

    source_type: Mapped[str] = mapped_column(
        String(20), default="auto", nullable=False
    )

    # 来源所属领域：AI、科技、财经
    category: Mapped[str] = mapped_column(
        String(20), default="科技", nullable=False
    )

    # 来源权重：1～5，默认 3
    weight: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
