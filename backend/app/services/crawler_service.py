"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 15:28:28
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:28:43
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.crawler_task import CrawlerTask


def create_crawler_task(db: Session) -> CrawlerTask:
    """创建采集任务"""

    task = CrawlerTask(status="pending", created_at=datetime.now())

    db.add(task)
    db.commit()
    db.refresh(task)

    return task



def update_crawler_task(
    db: Session,
    task_id: int,
    result: dict
) -> CrawlerTask | None:
    """更新采集任务结果"""

    task = db.query(CrawlerTask).filter(
        CrawlerTask.id == task_id
    ).first()

    if not task:
        return None

    task.status = "success"

    # 采集总数
    task.total = result.get("total_fetched", 0)

    # 成功入库数量
    task.saved = result.get("saved_count", 0)

    # 跳过数量：无效、无关、重复、数据库已存在
    task.skipped = (
        result.get("invalid_count", 0)
        + result.get("filtered_count", 0)
        + result.get("batch_duplicate_count", 0)
        + result.get("exists_count", 0)
    )

    # 记录部分保存失败的情况
    failed_count = result.get("failed_count", 0)

    if failed_count:
        task.error_message = f"有 {failed_count} 条新闻保存失败"
    else:
        task.error_message = None

    task.finished_at = datetime.now()

    db.commit()
    db.refresh(task)

    return task



def fail_crawler_task(
    db: Session, task_id: int, error_message: str
) -> CrawlerTask | None:
    """记录采集任务失败"""

    task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()

    if not task:
        return None

    task.status = "failed"
    task.error_message = error_message
    task.finished_at = datetime.now()

    db.commit()
    db.refresh(task)

    return task
def start_crawler_task(
    db: Session,
    task_id: int
) -> CrawlerTask | None:
    """将采集任务标记为运行中"""

    task = db.query(CrawlerTask).filter(
        CrawlerTask.id == task_id
    ).first()

    if not task:
        return None

    task.status = "running"
    task.started_at = datetime.now()

    db.commit()
    db.refresh(task)

    return task