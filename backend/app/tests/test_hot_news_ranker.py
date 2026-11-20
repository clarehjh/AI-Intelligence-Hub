"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 21:52:33
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:52:45
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.processors.hot_news_ranker import rank_hot_news

now = datetime.now(timezone.utc)

news_list = [
    SimpleNamespace(
        title="OpenAI releases a new model",
        source_weight=5,
        published_at=now - timedelta(hours=1),
        created_at=now,
    ),
    SimpleNamespace(
        title="A technology company raises funding",
        source_weight=3,
        published_at=now - timedelta(hours=24),
        created_at=now,
    ),
    SimpleNamespace(
        title="New GPU technology announced",
        source_weight=4,
        published_at=now - timedelta(hours=48),
        created_at=now,
    ),
]

result = rank_hot_news(news_list, limit=10)

for index, item in enumerate(result, start=1):
    print(index, item["news"].title, item["hot_score"])
