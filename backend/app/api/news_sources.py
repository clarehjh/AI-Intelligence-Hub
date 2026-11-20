"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 19:32:57
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 19:37:48
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.news_source import (
    NewsSourceCreate,
    NewsSourceUpdate,
    NewsSourceResponse,
)
from app.services.news_source_service import (
    create_news_source,
    get_news_sources,
    get_news_source_by_id,
    update_news_source,
    delete_news_source,
)

router = APIRouter(prefix="/news-sources", tags=["新闻来源管理"])


@router.post("", response_model=NewsSourceResponse)
def create_source(source_data: NewsSourceCreate, db: Session = Depends(get_db)):
    """添加新闻来源"""

    try:
        return create_news_source(db, source_data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[NewsSourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """查询新闻来源列表"""

    return get_news_sources(db)


@router.get("/{source_id}", response_model=NewsSourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """查询新闻来源详情"""

    source = get_news_source_by_id(db, source_id)

    if not source:
        raise HTTPException(status_code=404, detail="新闻来源不存在")

    return source


@router.put("/{source_id}", response_model=NewsSourceResponse)
def update_source(
    source_id: int, source_data: NewsSourceUpdate, db: Session = Depends(get_db)
):
    """修改新闻来源"""

    try:
        source = update_news_source(db, source_id, source_data)

        if not source:
            raise HTTPException(status_code=404, detail="新闻来源不存在")

        return source

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """删除新闻来源"""

    success = delete_news_source(db, source_id)

    if not success:
        raise HTTPException(status_code=404, detail="新闻来源不存在")

    return {"message": "新闻来源删除成功"}
