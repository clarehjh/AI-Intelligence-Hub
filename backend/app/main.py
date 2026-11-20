"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-18 18:50:07
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:08:29
"""

from fastapi import FastAPI
from app.api.routes import router
from app.config import settings
from app.database.init_db import init_db
from contextlib import asynccontextmanager
from app.api.crawler import router as crawler_router
from app.api.news_sources import router as news_sources_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    init_db()

    yield

    # 应用关闭时执行
    # 后续可以在这里释放数据库连接、关闭资源


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description="AI Intelligence Hub API",
    version="1.0.0",
)
# 注册业务路由
app.include_router(router)
app.include_router(crawler_router)
app.include_router(news_sources_router)
