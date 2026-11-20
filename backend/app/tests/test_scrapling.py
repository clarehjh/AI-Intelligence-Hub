
from scrapling.fetchers import Fetcher
from urllib.parse import urljoin
from backend.app.processors.news_cleaner import (
    process_news,
    remove_duplicate_news
)
# =========================
# 1. 抓取新闻首页
# =========================

def fetch_news_list(url):
    print("开始抓取新闻首页...")

    page = Fetcher.get(url)

    print("首页状态码：", page.status)
    print("首页标题：", page.css("title::text").get())

    news_cards = page.css("h2.wp-block-post-title")

    news_list = []

    for card in news_cards:
        link = card.css("a").first

        if not link:
            continue

        title = link.css("::text").get()
        news_url = link.attrib.get("href")

        if not title or not news_url:
            continue

        # 获取新闻卡片父级容器
        container = card.parent

        # 提取新闻摘要
        summary = container.css(
            ".featured-video-pattern__post-meta p::text"
        ).get()

        # 提取发布时间
        published_at = container.css(
            "time::attr(datetime)"
        ).get()

        news_item = {
            "title": title.strip(),
            "url": urljoin(url, news_url),
            "summary": summary.strip() if summary else "",
            "published_at": published_at,
            "content": "",
            "content_type": "article"
        }

        news_list.append(news_item)

    print(f"首页发现新闻数量：{len(news_list)}")

    return news_list


# =========================
# 2. 抓取新闻详情页
# =========================

def fetch_news_detail(url):
    print(f"\n开始抓取详情页：{url}")

    try:
        page = Fetcher.get(url)

        print("详情页状态码：", page.status)
        print("详情页标题：", page.css("title::text").get())

        # 获取正文容器
        content = page.css(".entry-content").first

        if not content:
            print("没有找到正文容器")
            return "", "unknown"

        # 判断是否为视频 / 播客内容
        video_description = content.css(
            'meta[itemprop="description"]::attr(content)'
        ).get()

        video_box = content.css(".jwppp-video-box")

        if video_description or len(video_box) > 0:
            if video_description:
                return video_description.strip(), "video"

        # 普通文章：提取段落文本
        paragraphs = content.css("p")

        text_list = []

        for paragraph in paragraphs:
            text_parts = paragraph.css("*::text").getall()

            full_text = " ".join(
                part.strip()
                for part in text_parts
                if part.strip()
            )

            if full_text:
                text_list.append(full_text)

        full_content = "\n".join(text_list)

        return full_content, "article"

    except Exception as e:
        print(f"详情页抓取失败：{e}")
        return "", "unknown"


# =========================
# 3. 主流程
# =========================

def main():

    # TechCrunch 首页
    home_url = "https://techcrunch.com/"

    # 第一步：抓取首页新闻列表
    news_list = fetch_news_list(home_url)
    # 对首页采集到的新闻进行去重
    news_list = remove_duplicate_news(news_list)

    print(f"去重后新闻数量：{len(news_list)}")
    # 第二步：逐条抓取详情页
    for index, news in enumerate(news_list, start=1):

        print(f"\n========== 新闻 {index} ==========")

        print("标题：", news["title"])
        print("摘要：", news["summary"])
        print("链接：", news["url"])
        print("发布时间：", news["published_at"])

        # 抓取详情页正文
        content, content_type = fetch_news_detail(news["url"])

        news["content"] = content
        news["content_type"] = content_type
        # 清洗并校验新闻
        cleaned_news = process_news(news) 
        if cleaned_news is None:
            print("新闻数据无效，跳过")
            continue   

        print("内容类型：", news["content_type"])
        print("正文：")
        print(news["content"][:1000])

        print("\n" + "=" * 50)

    # 第三步：查看最终采集结果
    print("\n采集任务完成！")
    print("总共采集新闻：", len(news_list))

    return news_list


if __name__ == "__main__":
    news_data = main()
