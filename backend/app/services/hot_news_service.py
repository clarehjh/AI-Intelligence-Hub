"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 21:54:39
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:55:39
"""

from sqlalchemy.orm import Session

from app.models.news import News
from app.processors.hot_news_ranker import rank_hot_news


def get_top_hot_news(db: Session, limit: int = 10) -> list[dict]:
    """
    从数据库获取新闻，并计算全局热点排名。
    """

    # 1. 查询数据库中的全部新闻
    news_list = db.query(News).all()

    # 2. 调用热点排名算法
    ranked_news = rank_hot_news(news_list, limit=limit)

    # 3. 整理返回结果
    result = []

    for index, item in enumerate(ranked_news, start=1):
        news = item["news"]

        result.append(
            {
                "rank": index,
                "hot_score": item["hot_score"],
                "id": news.id,
                "title": news.title,
                "source": news.source,
                "url": news.url,
                "summary": news.summary,
                "published_at": news.published_at,
            }
        )

    return result
