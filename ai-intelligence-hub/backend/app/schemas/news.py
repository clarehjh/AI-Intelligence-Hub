'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 19:12:57
LastEditors: Huangjiahui
LastEditTime: 2026-11-18 19:13:11
'''

from pydantic import BaseModel, HttpUrl

# 资讯请求数据结构
class NewsCreate(BaseModel):
    title: str
    source: str
    url: HttpUrl
