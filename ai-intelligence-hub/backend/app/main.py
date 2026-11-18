
from fastapi import FastAPI
from app.api.routes import router
from app.config import settings
from app.database.init_db import init_db
from contextlib import asynccontextmanager





@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    init_db()

    yield

    # 应用关闭时执行
    # 后续可以在这里释放数据库连接、关闭资源

app = FastAPI(lifespan=lifespan,  title=settings.APP_NAME, description="AI Intelligence Hub API", version="1.0.0")
# 注册业务路由
app.include_router(router)
