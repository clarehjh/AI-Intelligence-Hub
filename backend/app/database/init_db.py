"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 17:09:07
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 19:28:06
"""

"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-18 20:00:16
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:27:50

Base.metadata 保存所有继承 Base 的 ORM 模型对应的表结构信息。
create_all() 检查数据库中是否存在这些表，不存在就创建。
bind=engine 指定在哪个数据库中创建。
"""

from app.database.connection import Base, engine
from app.models.news import News
from app.models.crawler_task import CrawlerTask
from app.models.news_analysis_record import NewsAnalysisRecord
from app.models.news_source import NewsSource


def init_db():
    Base.metadata.create_all(bind=engine)
