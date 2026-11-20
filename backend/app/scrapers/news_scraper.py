from scrapling.fetchers import Fetcher
from urllib.parse import urljoin
from backend.app.processors.news_cleaner import process_news, remove_duplicate_news
from app.database.connection import SessionLocal
from app.services.news_service import create_news_if_not_exists
from datetime import datetime
from backend.app.processors.news_filter import filter_news

# =========================
# 1. 抓取新闻首页
# =========================


def fetch_news_list(url):
    print("开始抓取新闻首页...")

    page = Fetcher.get(url)

    print("首页状态码：", page.status)
    print("首页标题：", page.css("title::text").get())

    # 同时匹配原来的视频新闻标题和普通新闻标题
    news_cards = page.css("h2.wp-block-post-title, h3")

    news_list = []

    for card in news_cards:
        link = card.css("a").first

        if not link:
            continue

        title = link.css("::text").get()
        news_url = link.attrib.get("href")

        if not title or not news_url:
            continue

        # 过滤非新闻链接
        if "/20" not in news_url and "/video/" not in news_url:
            continue

        # 获取新闻卡片父级容器
        container = card.parent
        if (
            title.strip()
            == "Anthropic rival says companies can (mostly) skip the pricey models"
        ):

            print("\n========== 普通新闻节点诊断 ==========")

            current = card

            for level in range(1, 5):
                current = current.parent

                if not current:
                    break

                print(f"\n第 {level} 层父级 HTML：")
                print(current.get()[:3000])

            print("\n========== 诊断结束 ==========")
        if "/video/" in news_url:
            print("\n========== 摘要提取诊断 ==========")

            print("父级节点：")
            print(container.get())

            print("\n摘要容器数量：")
            print(len(container.css(".featured-video-pattern__post-meta")))

            print("\n段落数量：")
            print(len(container.css("p")))

            print("\n摘要文本 get()：")
            print(container.css(".featured-video-pattern__post-meta p::text").get())

            print("\n摘要文本 getall()：")
            print(container.css(".featured-video-pattern__post-meta p::text").getall())

            print("==================================")
        # 提取摘要
        summary = container.css(".featured-video-pattern__post-meta p::text").get()

        # 如果没有找到，尝试提取普通段落
        if not summary:
            summary = container.css("p::text").get()

        # 提取发布时间
        published_at = container.css("time::attr(datetime)").get()

        if published_at:
            try:
                published_at = datetime.fromisoformat(published_at)
            except ValueError:
                published_at = None

        # 调试输出：无论是否有发布时间都打印
        print("新闻标题：", title.strip())
        print("新闻摘要：", summary)
        print("发布时间：", published_at)
        print("-" * 50)
        news_item = {
            "title": title.strip(),
            "source": "TechCrunch",
            "url": urljoin(url, news_url),
            "summary": summary.strip() if summary else "",
            "published_at": published_at,
            "content": "",
            "content_type": "article",
        }

        news_list.append(news_item)

    print(f"首页原始匹配新闻数量：{len(news_list)}")

    # URL 去重
    news_list = remove_duplicate_news(news_list)

    print(f"首页去重后新闻数量：{len(news_list)}")
    # 筛选 AI 相关新闻
    news_list = filter_news(news_list, limit=15)
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

        # 提取文章摘要
        summary = (
            page.css('meta[property="og:description"]::attr(content)').get()
            or page.css('meta[name="description"]::attr(content)').get()
            or ""
        )

        # 获取正文容器
        content = page.css(".entry-content").first

        if not content:
            print("没有找到正文容器")
            return "", "unknown", summary

        # 判断是否为视频新闻
        video_description = content.css(
            'meta[itemprop="description"]::attr(content)'
        ).get()

        video_box = content.css(".jwppp-video-box")

        if video_description or len(video_box) > 0:
            if video_description:
                return video_description.strip(), "video", summary

        # 提取普通文章段落
        paragraphs = content.css("p")
        text_list = []

        for paragraph in paragraphs:
            text_parts = paragraph.css("*::text").getall()

            full_text = " ".join(part.strip() for part in text_parts if part.strip())

            if full_text:
                text_list.append(full_text)

        full_content = "\n".join(text_list)

        return full_content, "article", summary

    except Exception as e:
        print(f"详情页抓取失败：{e}")
        return "", "unknown", ""


# =========================
# 3. 主流程
# =========================


def main():
    db = SessionLocal()
    try:
        # TechCrunch 首页
        home_url = "https://techcrunch.com/"
        saved_count = 0
        skipped_count = 0
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
            content, content_type, summary = fetch_news_detail(news["url"])
            news["content"] = content
            news["content_type"] = content_type

            if not news.get("summary"):
                news["summary"] = summary
            # 清洗并校验新闻
            cleaned_news = process_news(news)
            if cleaned_news is None:
                skipped_count += 1
                print("新闻数据无效，跳过")
                continue

            saved_news = create_news_if_not_exists(db, cleaned_news)

            if saved_news:
                saved_count += 1
                print(f"新闻保存成功，ID：{saved_news.id}")
            else:
                skipped_count += 1
                print("新闻已存在，跳过保存")

            print("内容类型：", cleaned_news["content_type"])
            print("正文：")
            print(cleaned_news["content"][:1000])

            print("\n" + "=" * 50)

        # 第三步：查看最终采集结果
        print("\n采集任务完成！")
        print("总共采集新闻：", len(news_list))

        return {"total": len(news_list), "saved": saved_count, "skipped": skipped_count}
    finally:
        db.close()


if __name__ == "__main__":
    news_data = main()
