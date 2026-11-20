"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 21:21:47
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 21:22:11
"""

from sqlalchemy import text
from app.database.connection import engine


def migrate():
    with engine.begin() as conn:
        columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(news_sources)"))
        }

        if "category" not in columns:
            conn.execute(text("""
                    ALTER TABLE news_sources
                    ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT '科技'
                """))

        if "weight" not in columns:
            conn.execute(text("""
                    ALTER TABLE news_sources
                    ADD COLUMN weight INTEGER NOT NULL DEFAULT 3
                """))

    print("NewsSource 数据库迁移完成")


if __name__ == "__main__":
    migrate()
