import re


def clean_text(text: str) -> str:
    """清洗文本中的多余空格和换行"""

    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in text.split("\n")]

    text = "\n".join(lines)

    # 连续三个及以上换行压缩为两个
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_news(news: dict) -> dict:
    """清洗新闻数据"""

    return {
        **news,
        "title": clean_text(news.get("title", "")),
        "summary": clean_text(news.get("summary", "")),
        "content": clean_text(news.get("content", "")),
    }


def validate_news(news: dict) -> bool:
    """校验新闻数据"""

    if not news.get("title"):
        return False

    if not news.get("url"):
        return False

    return True


def process_news(news: dict) -> dict | None:
    """清洗并校验一条新闻"""

    cleaned_news = clean_news(news)

    if not validate_news(cleaned_news):
        return None

    return cleaned_news


def remove_duplicate_news(news_list: list[dict]) -> list[dict]:
    """根据新闻 URL 去重"""

    seen_urls = set()
    result = []

    for news in news_list:
        url = news.get("url")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        result.append(news)

    return result
