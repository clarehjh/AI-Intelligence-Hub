"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 21:51:25
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:51:42
"""

from datetime import datetime, timezone


def calculate_time_score(published_at: datetime | None, now: datetime) -> float:
    """
    根据新闻发布时间计算时效分数。
    24 小时衰减一半。
    """

    if not published_at:
        return 0

    # 统一处理时区，避免 datetime 比较报错
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    age_hours = max(0, (now - published_at).total_seconds() / 3600)

    return 100 * (0.5 ** (age_hours / 24))


def calculate_hot_score(news, now: datetime | None = None) -> float:
    """
    计算单条新闻的热点代理分数。
    """

    if now is None:
        now = datetime.now(timezone.utc)

    # 来源权重 1～5，转换成 0～100
    source_weight = getattr(news, "source_weight", 3) or 3
    source_score = source_weight / 5 * 100

    # 优先使用新闻发布时间，没有则使用入库时间
    published_at = getattr(news, "published_at", None) or getattr(
        news, "created_at", None
    )

    time_score = calculate_time_score(published_at, now)

    hot_score = 0.6 * source_score + 0.4 * time_score

    return round(hot_score, 2)


def rank_hot_news(news_list: list, limit: int = 10) -> list[dict]:
    """
    对新闻进行热点代理评分，返回排名前 N 的新闻。
    """

    now = datetime.now(timezone.utc)

    ranked_news = []

    for news in news_list:
        score = calculate_hot_score(news, now)

        ranked_news.append({"news": news, "hot_score": score})

    ranked_news.sort(key=lambda item: item["hot_score"], reverse=True)

    return ranked_news[:limit]
