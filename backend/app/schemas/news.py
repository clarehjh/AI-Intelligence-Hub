"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 17:09:07
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:49:46
"""

from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict


class NewsCreate(BaseModel):
    """创建新闻"""

    title: str
    source: str
    source_category: str = "科技"
    source_weight: int = 3
    url: HttpUrl
    summary: str | None = None
    content: str | None = None


class NewsResponse(BaseModel):
    """新闻响应"""

    id: int
    title: str
    source: str
    source_category: str
    source_weight: int
    url: str
    summary: str | None = None
    content: str | None = None
    content_type: str
    published_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsUpdate(BaseModel):
    """更新新闻"""

    title: str | None = None
    source: str | None = None
    source_category: str | None = None
    source_weight: int | None = None
    url: HttpUrl | None = None
    summary: str | None = None
    content: str | None = None
