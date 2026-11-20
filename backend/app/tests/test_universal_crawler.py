from app.database.connection import SessionLocal
from app.services.universal_crawler_service import (
    crawl_and_save_enabled_sources,
)


def main():
    db = SessionLocal()

    try:
        result = crawl_and_save_enabled_sources(db)

        print("\n最终执行结果：")
        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
