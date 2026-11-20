from sqlalchemy.orm import Session
from app.models.news import News


def news_exists(db: Session, url: str) -> bool:
    """判断新闻是否已经存在于数据库"""

    news = db.query(News).filter(News.url == url).first()

    return news is not None



def save_news(db: Session, news_data: dict) -> News:
    """
    将新闻保存到数据库
    """

    news = News(**news_data)

    db.add(news)
    db.commit()
    db.refresh(news)

    return news

def create_news_if_not_exists(
    db: Session,
    news_data: dict
) -> News | None:
    """新闻不存在时保存，已存在则跳过"""

    url = news_data.get("url")

    if not url:
        return None

    if news_exists(db, url):
        return None

    return save_news(db, news_data)