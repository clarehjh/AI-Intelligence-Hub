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
import asyncio
from app.models.news import News
from app.models.news_analysis_record import NewsAnalysisRecord
from app.services.news_agent import analyze_news
from app.config import settings
from app.services.hot_news_service import get_top_hot_news


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

            failed_news.append(
                {"news_id": news.id, "title": news.title, "error": str(e)}
            )

    # 4. 返回批量分析结果
    return {
        "total": len(news_list),
        "success": success_count,
        "failed": failed_count,
        "failed_news": failed_news,
    }



# asyncio.to_thread()：把同步阻塞函数放到线程中运行。
# asyncio.Semaphore(3)：限制最多三个模型请求同时执行。
# asyncio.gather()：并发执行多个协程，并等待结果。
async def analyze_hot_news(db: Session, limit: int = 10):
    """并发分析全局热点新闻，最多同时请求 3 条"""

    # 1. 获取热点新闻
    hot_news_list = get_top_hot_news(db, limit=limit)

    # 2. 查询已经分析过的新闻
    news_ids = [item["id"] for item in hot_news_list]

    existing_records = (
        db.query(NewsAnalysisRecord)
        .filter(NewsAnalysisRecord.news_id.in_(news_ids))
        .all()
    )

    analyzed_ids = {record.news_id for record in existing_records}

    # 3. 筛选待分析新闻
    pending_news = []

    for item in hot_news_list:
        if item["id"] in analyzed_ids:
            continue

        news = db.query(News).filter(News.id == item["id"]).first()

        if news:
            pending_news.append((item, news))

    # 4. 设置最大并发数
    semaphore = asyncio.Semaphore(3)

    async def analyze_one(item, news):
        """在线程中执行同步模型请求"""

        try:
            if news.summary:
                content = ""
            else:
                content = (news.content or "")[:3000]

            async with semaphore:
                analysis = await asyncio.to_thread(
                    analyze_news,
                    title=news.title,
                    summary=news.summary or "",
                    content=content,
                )

            return item, analysis, None

        except Exception as e:
            return item, None, str(e)

    # 5. 并发执行模型分析
    tasks = [analyze_one(item, news) for item, news in pending_news]

    results = await asyncio.gather(*tasks)

    # 6. 依次保存分析结果
    success_count = 0
    failed_count = 0
    failed_news = []

    for item, analysis, error in results:
        if error:
            failed_count += 1
            failed_news.append(
                {
                    "news_id": item["id"],
                    "title": item["title"],
                    "error": error,
                }
            )
            continue
        if analysis is None:
            failed_count += 1
            failed_news.append({
                "news_id": item["id"],
                "title": item["title"],
                "error": "模型没有返回分析结果",
            })
            continue
        try:
            record = NewsAnalysisRecord(
                news_id=item["id"],
                result=analysis.model_dump(),
                model_name=settings.LLM_MODEL,
                analyzed_at=datetime.now(),
            )

            db.add(record)
            db.commit()

            success_count += 1

        except Exception as e:
            db.rollback()
            failed_count += 1

            failed_news.append(
                {
                    "news_id": item["id"],
                    "title": item["title"],
                    "error": str(e),
                }
            )

    # 7. 返回统计结果
    skipped_count = len(hot_news_list) - len(pending_news)

    return {
        "total": len(hot_news_list),
        "success": success_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "failed_news": failed_news,
    }
