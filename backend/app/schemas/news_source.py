
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["auto", "rss", "sitemap", "website"]

NewsCategory = Literal["AI", "科技", "财经"]


class NewsSourceCreate(BaseModel):
    """创建新闻来源"""

    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=1000)
    source_type: SourceType = "auto"
    category: NewsCategory = "科技"
    weight: int = Field(default=3, ge=1, le=5)
    enabled: bool = True


class NewsSourceUpdate(BaseModel):
    """更新新闻来源"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    url: str | None = Field(default=None, min_length=1, max_length=1000)
    source_type: SourceType | None = None
    category: NewsCategory | None = None
    weight: int | None = Field(default=None, ge=1, le=5)
    enabled: bool | None = None


class NewsSourceResponse(BaseModel):
    """新闻来源响应"""

    id: int
    name: str
    url: str
    source_type: str
    category: str
    weight: int
    enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
