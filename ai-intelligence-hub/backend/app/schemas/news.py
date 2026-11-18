'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 19:12:57
LastEditors: Huangjiahui
LastEditTime: 2026-11-18 21:02:34
'''

from pydantic import BaseModel, HttpUrl,ConfigDict
from datetime import datetime

# 资讯请求数据结构
class NewsCreate(BaseModel):
    title: str
    source: str
    url: HttpUrl
    content: str
class NewsResponse(BaseModel):
    id: int
    title: str
    source: str
    url: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)#它允许 Pydantic 从 SQLAlchemy ORM 对象的属性中读取数据，而不只是从字典中读取

