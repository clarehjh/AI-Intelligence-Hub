"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-18 18:58:08
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:05:13
"""

"""
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 18:58:08
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 12:13:47
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.news import NewsCreate, NewsResponse, NewsUpdate
from app.models.news import News
from app.database.dependencies import get_db
from app.services.hot_news_service import get_top_hot_news
from app.services.news_analysis_service import (
    analyze_news_by_id,
    get_news_analysis,
    analyze_hot_news,
)

# 创建路由对象
router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome to AI Intelligence Hub!", "status": "success"}


@router.get("/health")
async def health():
    return {"status": "healthy"}


"""
1. db.add(db_news)：将 ORM 对象添加到当前 Session。
2. db.commit()：提交事务，将数据真正保存到数据库。
3. db.refresh(db_news)：从数据库重新读取对象，获取数据库生成的 ID、创建时间等字段。
这里还有一个细节：response_model=NewsResponse 会让 FastAPI 使用 Pydantic 模型校验并序列化返回值。
"""


@router.post("/news", response_model=NewsResponse)
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    db_news = News(
        title=news.title, source=news.source, url=str(news.url), content=news.content
    )

    db.add(db_news)
    db.commit()
    db.refresh(db_news)

    return db_news


@router.get("/news", response_model=list[NewsResponse])
def get_news(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):

    news_list = db.query(News).offset(skip).limit(limit).all()
    return news_list


@router.get("/news/hot")
def get_hot_news(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取热点新闻排行榜"""

    news_list = get_top_hot_news(db, limit=limit)

    return {
        "total": len(news_list),
        "items": news_list,
    }


@router.get("/news/{news_id}", response_model=NewsResponse)
def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    # 在这里完成查询
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    return news_item


@router.put("/news/{news_id}", response_model=NewsResponse)
def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db)):
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")

    # 更新新闻条目
    # news_item.title = news.title
    # news_item.source = news.source
    # news_item.url = str(news.url)
    # news_item.content = news.content

    update_data = news.model_dump()
    update_data["url"] = str(news.url)
    for key, value in update_data.items():
        setattr(news_item, key, value)

    db.commit()
    db.refresh(news_item)
    return news_item


@router.delete("/news/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    # 自己完成删除逻辑
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    db.delete(news_item)
    db.commit()
    return {"message": "News item deleted successfully"}


@router.post("/news/hot/analyze")
async def analyze_hot_news_api(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = await analyze_hot_news(db, limit=limit)

    return {
        "message": "热点新闻分析完成",
        **result,
    }


# 分析新闻
@router.post("/news/{news_id}/analyze")
def analyze_news_api(news_id: int, db: Session = Depends(get_db)):
    record = analyze_news_by_id(db, news_id)

    if not record:
        raise HTTPException(status_code=404, detail="News item not found")

    return {
        "id": record.id,
        "news_id": record.news_id,
        "model_name": record.model_name,
        "analyzed_at": record.analyzed_at,
        "result": record.result,
    }


@router.get("/news/{news_id}/analysis")
def get_news_analysis_api(news_id: int, db: Session = Depends(get_db)):
    record = get_news_analysis(db, news_id)

    if not record:
        raise HTTPException(status_code=404, detail="News analysis not found")

    return {
        "id": record.id,
        "news_id": record.news_id,
        "model_name": record.model_name,
        "analyzed_at": record.analyzed_at,
        "result": record.result,
    }
