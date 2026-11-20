import threading
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.dependencies import get_db
from app.scrapers.news_scraper import main
from app.services.crawler_service import (
    create_crawler_task,
    start_crawler_task,
    update_crawler_task,
    fail_crawler_task,
)
from app.models.crawler_task import CrawlerTask

router = APIRouter(prefix="/crawler", tags=["新闻采集"])

crawler_lock = threading.Lock()

crawler_status = {
    "running": False,
    "last_run": None,
    "message": "尚未执行采集",
    "total": 0,
    "saved": 0,
    "skipped": 0,
}


def run_crawler_task(task_id: int):
    """后台执行新闻采集任务"""

    db = SessionLocal()

    try:
        start_crawler_task(db, task_id)

        result = main()

        update_crawler_task(db, task_id, result)

        crawler_status.update(
            {
                "last_run": datetime.now().isoformat(),
                "total": result["total"],
                "saved": result["saved"],
                "skipped": result["skipped"],
                "message": "采集完成",
            }
        )

    except Exception as e:
        db.rollback()
        fail_crawler_task(db, task_id, str(e))

        crawler_status["message"] = f"采集失败：{str(e)}"

    finally:
        db.close()

        with crawler_lock:
            crawler_status["running"] = False


@router.post("/run")
def start_crawler(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """手动启动新闻采集"""

    with crawler_lock:
        if crawler_status["running"]:
            return {"message": "采集任务正在执行中"}

        task = create_crawler_task(db)

        crawler_status["running"] = True
        crawler_status["message"] = "新闻正在采集中"

    background_tasks.add_task(run_crawler_task, task.id)

    return {"message": "新闻采集任务已启动", "task_id": task.id}


@router.get("/status")
def get_crawler_status():
    """获取最近一次采集状态"""
    return crawler_status


@router.get("/tasks")
def get_crawler_tasks(db: Session = Depends(get_db)):
    """查询采集任务历史"""

    tasks = db.query(CrawlerTask).order_by(CrawlerTask.id.desc()).limit(20).all()

    return tasks


@router.get("/tasks/{task_id}")
def get_crawler_task(task_id: int, db: Session = Depends(get_db)):
    """根据 ID 查询采集任务"""

    task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Crawler task not found")

    return task
