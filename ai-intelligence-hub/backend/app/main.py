
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Intelligence Hub",
    description="个人 AI 情报中心 API",
    version="1.0.0"
)

# 注册业务路由
app.include_router(router)
