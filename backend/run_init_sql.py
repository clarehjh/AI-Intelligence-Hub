
import sqlite3

db_path = "data/ai_hub.db"

conn = sqlite3.connect(db_path)

try:
    with open("init.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    conn.executescript(sql)
    conn.commit()

    print("初始化 SQL 执行成功！")

except Exception as e:
    conn.rollback()
    print(f"初始化失败：{e}")

finally:
    conn.close()
