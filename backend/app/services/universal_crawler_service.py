"""
Description: 多来源新闻采集与入库服务
Author: Huangjiahui
"""

from sqlalchemy.orm import Session

from app.models.news_source import NewsSource
from app.scrapers.universal_crawler import fetch_source_news
from app.processors.news_cleaner import (
    process_news,
    remove_duplicate_news,
)
from app.processors.news_filter import filter_news
from app.services.news_service import create_news_if_not_exists


def fetch_enabled_sources_news(db: Session) -> list[dict]:
    """采集所有已启用新闻来源的新闻"""

    sources = db.query(NewsSource).filter(NewsSource.enabled.is_(True)).all()

    all_news = []

    for source in sources:
        print(f"开始采集：{source.name}")

        try:
            news_list = fetch_source_news(
                url=source.url,
                source_type=source.source_type,
            )

            # 为每条新闻补充来源信息
            for news in news_list:
                news["source"] = source.name
                news["source_category"] = source.category
                news["source_weight"] = source.weight

            all_news.extend(news_list)

            print(
                f"{source.name}：采集到 {len(news_list)} 条新闻，"
                f"领域：{source.category}，权重：{source.weight}"
            )

        except Exception as e:
            print(f"{source.name} 采集失败：{e}")
            continue

    print(f"所有来源采集完成，共获取 {len(all_news)} 条新闻")

    return all_news


def crawl_and_save_enabled_sources(db: Session) -> dict:
    """采集新闻、清洗、过滤、去重并保存到数据库"""

    # 1. 采集新闻
    all_news = fetch_enabled_sources_news(db)

    # 2. 清洗和校验
    cleaned_news = []
    invalid_count = 0

    for news in all_news:
        result = process_news(news)

        if result is None:
            invalid_count += 1
            continue

        cleaned_news.append(result)

    # 3. 过滤不相关领域的新闻
    filtered_news = filter_news(cleaned_news)
    filtered_count = len(cleaned_news) - len(filtered_news)

    # 4. 对本次采集的数据进行 URL 去重
    unique_news = remove_duplicate_news(filtered_news)
    batch_duplicate_count = len(filtered_news) - len(unique_news)

    # 5. 保存新闻
    saved_count = 0
    exists_count = 0
    failed_count = 0

    for news in unique_news:
        try:
            saved = create_news_if_not_exists(db, news)

            if saved is not None:
                saved_count += 1
                print(f"新闻保存成功：{news['title']}")
            else:
                exists_count += 1
                print(f"新闻已存在，跳过：{news['title']}")

        except Exception as e:
            db.rollback()
            failed_count += 1
            print(f"新闻保存失败：{news.get('title')}，原因：{e}")

    # 6. 汇总结果
    result = {
        "total_fetched": len(all_news),
        "valid_count": len(cleaned_news),
        "invalid_count": invalid_count,
        "filtered_count": filtered_count,
        "batch_duplicate_count": batch_duplicate_count,
        "saved_count": saved_count,
        "exists_count": exists_count,
        "failed_count": failed_count,
    }

    print("\n========== 新闻采集结果 ==========")
    print(f"采集总数：{result['total_fetched']}")
    print(f"有效新闻：{result['valid_count']}")
    print(f"无效新闻：{result['invalid_count']}")
    print(f"过滤无关新闻：{result['filtered_count']}")
    print(f"本批次重复：{result['batch_duplicate_count']}")
    print(f"新增入库：{result['saved_count']}")
    print(f"数据库已存在：{result['exists_count']}")
    print(f"保存失败：{result['failed_count']}")
    print("==================================")

    return result
