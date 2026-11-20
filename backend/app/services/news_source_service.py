"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 19:30:01
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 19:30:14
"""

from sqlalchemy.orm import Session

from app.models.news_source import NewsSource
from app.schemas.news_source import NewsSourceCreate, NewsSourceUpdate


def create_news_source(db: Session, source_data: NewsSourceCreate):
    """创建新闻来源"""

    # 检查 URL 是否已经存在
    existing = db.query(NewsSource).filter(NewsSource.url == source_data.url).first()

    if existing:
        raise ValueError("该新闻来源已经存在")

    source = NewsSource(**source_data.model_dump())

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def get_news_sources(db: Session):
    """查询所有新闻来源"""

    return db.query(NewsSource).order_by(NewsSource.id.desc()).all()


def get_news_source_by_id(db: Session, source_id: int):
    """根据 ID 查询新闻来源"""

    return db.query(NewsSource).filter(NewsSource.id == source_id).first()


def update_news_source(db: Session, source_id: int, source_data: NewsSourceUpdate):
    """更新新闻来源"""

    source = get_news_source_by_id(db, source_id)

    if not source:
        return None

    update_data = source_data.model_dump(exclude_unset=True, exclude_none=True)

    # 如果修改了 URL，检查是否与其他来源重复
    new_url = update_data.get("url")

    if new_url:
        existing = (
            db.query(NewsSource)
            .filter(NewsSource.url == new_url, NewsSource.id != source_id)
            .first()
        )

        if existing:
            raise ValueError("该新闻来源 URL 已经存在")

    for key, value in update_data.items():
        setattr(source, key, value)

    db.commit()
    db.refresh(source)

    return source


def delete_news_source(db: Session, source_id: int):
    """删除新闻来源"""

    source = get_news_source_by_id(db, source_id)

    if not source:
        return False

    db.delete(source)
    db.commit()

    return True
