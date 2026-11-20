'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-20 14:26:09
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 14:26:22
'''
from app.database.connection import SessionLocal
from app.services.news_service import create_news_if_not_exists


db = SessionLocal()

try:
    news_data = {
        "title": "AI Agent 测试新闻",
        "source": "TechCrunch",
        "url": "https://example.com/test-news-001",
        "summary": "这是一条测试摘要",
        "content": "这是一条测试新闻正文",
        "content_type": "article"
    }

    result = create_news_if_not_exists(db, news_data)

    if result:
        print("新闻保存成功：", result.id)
    else:
        print("新闻已存在或数据不完整")

finally:
    db.close()