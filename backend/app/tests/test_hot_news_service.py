"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 21:56:20
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:56:31
"""

from app.database.connection import SessionLocal
from app.services.hot_news_service import get_top_hot_news

db = SessionLocal()

try:
    result = get_top_hot_news(db, limit=10)

    for news in result:
        print(
            f"排名：{news['rank']} | "
            f"分数：{news['hot_score']} | "
            f"标题：{news['title']} | "
            f"来源：{news['source']}"
        )

finally:
    db.close()
