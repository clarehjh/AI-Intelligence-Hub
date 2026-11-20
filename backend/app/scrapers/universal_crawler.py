"""
Description: 通用新闻采集器，支持 RSS 2.0 和 Atom
Version: 1.0
Author: Huangjiahui
Date: 2026-11-20
LastEditors: Huangjiahui
LastEditTime: 2026-11-20
"""

from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from scrapling.fetchers import Fetcher
from datetime import datetime
import re
from html import unescape


def clean_rss_text(text: str) -> str:
    """清洗 RSS 中的 HTML 和特殊字符"""

    if not text:
        return ""

    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", " ", text)

    # 还原 HTML 实体
    text = unescape(text)

    # 合并多余空白
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def discover_rss_url(url: str) -> str | None:
    """自动发现网站的 RSS / Atom 地址"""

    try:
        page = Fetcher.get(url)

        # 查找网站声明的 RSS 和 Atom 地址
        selectors = [
            'link[type="application/rss+xml"]::attr(href)',
            'link[type="application/atom+xml"]::attr(href)',
        ]

        for selector in selectors:
            rss_urls = page.css(selector).getall()

            if rss_urls:
                # 将相对路径转换成完整 URL
                rss_url = urljoin(url, rss_urls[0])
                return rss_url

        return None

    except Exception as e:
        print(f"发现 RSS 地址失败：{e}")
        return None


def fetch_rss_news(rss_url: str) -> list[dict]:
    """获取 RSS / Atom 新闻列表"""

    try:
        response = Fetcher.get(rss_url)

        body = response.body

        # 统一转换为字符串
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")

    
        if body.lstrip().lower().startswith(("<!doctype html", "<html")):
            print(f"采集地址返回的是 HTML，不是 RSS：{rss_url}")
            return []
        root = ET.fromstring(body)

        news_list = []

        # 判断是否为 Atom 格式
        if root.tag.endswith("feed"):

            namespace = {"atom": "http://www.w3.org/2005/Atom"}

            items = root.findall("atom:entry", namespace)

            for item in items:

                title = item.findtext("atom:title", default="", namespaces=namespace)

                summary = item.findtext(
                    "atom:summary", default="", namespaces=namespace
                )

                # Atom 的 link 存储在 href 属性中
                # 优先选择文章的 alternate 链接
                link = ""

                for link_element in item.findall("atom:link", namespace):
                    rel = link_element.get("rel", "alternate")

                    if rel == "alternate":
                        link = link_element.get("href", "")
                        break

                # 获取发布时间
                pub_date = item.findtext(
                    "atom:published", namespaces=namespace
                ) or item.findtext("atom:updated", namespaces=namespace)

                published_at = None

                if pub_date:
                    try:
                        published_at = datetime.fromisoformat(
                            pub_date.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                news_list.append(
                    {
                        "title": clean_rss_text(title),
                        "url": urljoin(rss_url, link),
                        "summary": clean_rss_text(summary),
                        "published_at": published_at,
                        "content": "",
                        "content_type": "article",
                    }
                )

        else:
            # RSS 2.0 格式
            items = root.findall(".//item")

            for item in items:

                title = item.findtext("title", default="")
                link = item.findtext("link", default="")
                summary = item.findtext("description", default="")
                pub_date = item.findtext("pubDate")

                published_at = None

                if pub_date:
                    try:
                        published_at = parsedate_to_datetime(pub_date)
                    except (TypeError, ValueError):
                        pass

                news_list.append(
                    {
                        "title": clean_rss_text(title),
                        "url": urljoin(rss_url, link.strip()),
                        "summary": clean_rss_text(summary),
                        "published_at": published_at,
                        "content": "",
                        "content_type": "article",
                    }
                )

        # 过滤掉没有标题或链接的数据
        news_list = [news for news in news_list if news["title"] and news["url"]]

        return news_list

    except Exception as e:
        print(f"RSS / Atom 新闻解析失败：{e}")
        return []


def fetch_source_news(url: str, source_type: str = "auto") -> list[dict]:
    """
    根据新闻来源类型，选择对应的采集方式。
    """

    # 自动发现 RSS
    if source_type == "auto":

        rss_url = discover_rss_url(url)

        if not rss_url:
            print(f"未发现 RSS：{url}")
            return []

        return fetch_rss_news(rss_url)

    # 指定 RSS 地址
    if source_type == "rss":
        return fetch_rss_news(url)

    # 其他类型暂时不支持
    print(f"暂不支持的采集类型：{source_type}")

    return []


def debug_website(url: str):
    """调试网站首页，查看标题和链接"""

    page = Fetcher.get(url)

    print("\n网页标题：")
    print(page.css("title::text").get())

    print("\n网页中的链接：")

    links = page.css("a")

    for link in links[:30]:
        title = link.css("::text").get()
        href = link.attrib.get("href", "")

        if title and href:
            print(title.strip(), href)


def inspect_article_page(url: str):
    """检查文章页面的 HTML 结构"""

    page = Fetcher.get(url)

    print("网页标题：", page.css("title::text").get())

    # 检查文章相关的 HTML 元素
    for selector in ["article", "h1", "h2", "h3"]:

        elements = page.css(selector)

        print(f"\n{selector} 数量：{len(elements)}")

        for element in elements[:10]:
            text = element.css("::text").getall()
            print("文本：", " ".join(text).strip()[:150])

    # 专门检查文章详情链接
    links = page.css('a[href*="/articles/"]')

    print(f"\n文章详情链接数量：{len(links)}")

    for link in links[:20]:
        title = " ".join(link.css("::text").getall()).strip()
        href = link.attrib.get("href", "")

        print(title, href)


if __name__ == "__main__":

    test_url = "https://techcrunch.com/"

    # 1. 自动发现 RSS 地址
    rss_url = discover_rss_url(test_url)

    print("发现的 RSS 地址：", rss_url)

    if rss_url:

        # 2. 获取 RSS 新闻
        news_list = fetch_rss_news(rss_url)

        print(f"\n成功获取 {len(news_list)} 条新闻")

        # 3. 打印前 3 条新闻
        for news in news_list[:3]:

            print("\n--------------------")
            print("标题：", news["title"])
            print("链接：", news["url"])
            print("摘要：", news["summary"][:150])
            print("发布时间：", news["published_at"])
