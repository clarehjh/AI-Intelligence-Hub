'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 18:58:08
LastEditors: Huangjiahui
LastEditTime: 2026-11-18 19:14:15
'''

from fastapi import APIRouter
from app.schemas.news import NewsCreate

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
@router.post("/news")
async def create_news(news: NewsCreate):
    return {
        "message": "资讯创建成功",
        "data": news.model_dump(mode="json")
        #是把 Pydantic 对象转换为适合 JSON 响应的 Python 字典，其中 HttpUrl 也会转换为字符串。
    }