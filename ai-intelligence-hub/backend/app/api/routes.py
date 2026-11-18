'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 18:58:08
LastEditors: Huangjiahui
LastEditTime: 2026-11-18 21:12:43
'''

from fastapi import APIRouter, Depends
from sqlalchemy.orm   import Session
from app.schemas.news import NewsCreate, NewsResponse
from app.models.news import News
from app.database.dependencies import get_db
# 创建路由对象
router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Welcome to AI Intelligence Hub!",
        "status": "success"
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }





'''
1. db.add(db_news)：将 ORM 对象添加到当前 Session。
2. db.commit()：提交事务，将数据真正保存到数据库。
3. db.refresh(db_news)：从数据库重新读取对象，获取数据库生成的 ID、创建时间等字段。
这里还有一个细节：response_model=NewsResponse 会让 FastAPI 使用 Pydantic 模型校验并序列化返回值。
'''
@router.post("/news", response_model=NewsResponse)
def create_news(
    news: NewsCreate,
    db: Session = Depends(get_db)
):
    db_news = News(
        title=news.title,
        source=news.source,
        url=str(news.url),
        content=news.content
    )

    db.add(db_news)
    db.commit()
    db.refresh(db_news)

    return db_news

@router.get("/news", response_model=list[NewsResponse])
def get_news(db: Session = Depends(get_db)):
    news_list = db.query(News).all()
    return news_list