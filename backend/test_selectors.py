"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 15:56:01
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 15:56:20
"""

from scrapling.fetchers import Fetcher

url = "https://techcrunch.com/"

print("正在请求 TechCrunch 首页...")
page = Fetcher.get(url)

print("HTTP 状态码：", page.status)
print("网页标题：", page.css("title::text").get())

# 测试不同的标题选择器
selectors = [
    "h2.wp-block-post-title",
    "h3.wp-block-post-title",
    ".wp-block-post-title",
    "h2",
    "h3",
]

print("\n========== CSS 选择器匹配结果 ==========")

for selector in selectors:
    elements = page.css(selector)

    print(f"\n选择器：{selector}")
    print(f"匹配数量：{len(elements)}")

    for index, element in enumerate(elements[:5], start=1):
        title = element.css("a::text").get()
        href = element.css("a::attr(href)").get()

        print(f"{index}. 标题：{title}")
        print(f"   链接：{href}")

# 查看页面中所有新闻标题相关的 HTML
print("\n========== 包含 post-title 的 HTML ==========")

elements = page.css('[class*="post-title"]')

print("匹配数量：", len(elements))

for element in elements[:10]:
    print(element.get())

print("\n========== H3 新闻标题分析 ==========")

elements = page.css("h3")

count = 0

for element in elements:
    link = element.css("a").first

    if not link:
        continue

    title = link.css("::text").get()
    href = link.attrib.get("href")

    if not title or not href:
        continue

    count += 1

    print(f"\n新闻 {count}")
    print("标题：", title.strip())
    print("链接：", href)

print("\nH3 中有效链接数量：", count)

print("========== 新闻卡片摘要测试 ==========")

for selector in ["h3", "h2.wp-block-post-title"]:
    elements = page.css(selector)

    for card in elements:
        link = card.css("a").first

        if not link:
            continue

        title = link.css("::text").get()
        href = link.attrib.get("href")

        if not title or not href:
            continue

        container = card.parent

        print("\n标题：", title.strip())
        print("链接：", href)
        print("父级 HTML：")
        print(container.get()[:2000])
        print("-" * 60)
