"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 18:20:25
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 18:20:40
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.news import News
from app.models.news_analysis_record import NewsAnalysisRecord
from app.services.news_agent import analyze_news
from app.config import settings


def analyze_news_by_id(db: Session, news_id: int):
    # 1. 根据 ID 查询新闻
    news = db.query(News).filter(News.id == news_id).first()

    # 2. 新闻不存在时，返回 None
    if not news:
        return None
    print("标题长度：", len(news.title))
    print("摘要长度：", len(news.summary or ""))
    print("正文长度：", len(news.content or ""))
    # 3. 调用 Agent 分析新闻
    # 优先使用新闻摘要，避免传入过长正文
    if news.summary:
        content = ""
    else:
        content = (news.content or "")[:3000]

    analysis = analyze_news(
        title=news.title, summary=news.summary or "", content=content
    )
    # analysis = analyze_news(
    #     title=news.title, summary=news.summary or "", content=news.content or ""
    # )
    # 4. 将 Pydantic 对象转换为字典
    analysis_data = analysis.model_dump()

    # 5. 查询是否已经存在分析记录
    record = (
        db.query(NewsAnalysisRecord)
        .filter(NewsAnalysisRecord.news_id == news_id)
        .first()
    )

    if record:
        # 已存在：更新分析结果
        record.result = analysis_data
        record.model_name = settings.LLM_MODEL
        record.analyzed_at = datetime.now()
    else:
        # 不存在：创建新记录
        record = NewsAnalysisRecord(
            news_id=news_id, result=analysis_data, model_name=settings.LLM_MODEL
        )
        db.add(record)

    # 6. 提交事务
    db.commit()
    db.refresh(record)

    return record


def get_news_analysis(db: Session, news_id: int):
    record = (
        db.query(NewsAnalysisRecord)
        .filter(NewsAnalysisRecord.news_id == news_id)
        .first()
    )

    return record


def get_unanalyzed_news(db: Session, limit: int = 10):
    news_list = (
        db.query(News)
        .outerjoin(NewsAnalysisRecord, News.id == NewsAnalysisRecord.news_id)
        .filter(NewsAnalysisRecord.id.is_(None))
        .order_by(News.id.asc())
        .limit(limit)
        .all()
    )

    return news_list



def analyze_pending_news(db: Session, limit: int = 10):
    # 1. 查询待分析新闻
    news_list = get_unanalyzed_news(db, limit)

    # 2. 初始化统计数据
    success_count = 0
    failed_count = 0
    failed_news = []

    # 3. 逐条调用 Agent
    for news in news_list:
        try:
            analyze_news_by_id(db, news.id)
            success_count += 1

        except Exception as e:
            db.rollback()
            failed_count += 1

            failed_news.append({
                "news_id": news.id,
                "title": news.title,
                "error": str(e)
            })

    # 4. 返回批量分析结果
    return {
        "total": len(news_list),
        "success": success_count,
        "failed": failed_count,
        "failed_news": failed_news
    }
