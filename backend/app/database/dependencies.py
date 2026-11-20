'''
Description: 
version: 
Author: Huangjiahui
Date: 2026-11-18 20:14:12
LastEditors: Huangjiahui
LastEditTime: 2026-11-18 20:15:25
'''
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  #yield db：把 Session 交给接口使用
    finally:
        db.close()