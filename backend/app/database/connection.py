
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

# 1. 从配置中读取数据库连接地址
DATABASE_URL = settings.DATABASE_URL


# 2. 创建数据库引擎
# SQLite 使用 check_same_thread=False，因为 FastAPI 的请求可能由不同线程处理。
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# 3. 定义 ORM 模型基类
class Base(DeclarativeBase):
    pass


# 4. 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
