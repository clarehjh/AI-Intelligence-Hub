# AI 领域关键词
AI_KEYWORDS = [
    "artificial intelligence",
    "generative ai",
    "large language model",
    "large language models",
    "llm",
    "agent",
    "agents",
    "openai",
    "anthropic",
    "chatgpt",
    "claude",
    "gemini",
    "deepseek",
    "rag",
    "mcp",
    "langchain",
    "langgraph",
    "machine learning",
    "deep learning",
    "人工智能",
    "大模型",
    "智能体",
    "生成式人工智能",
    "机器学习",
    "深度学习",
    "多模态",
    "具身智能",
]

# 科技领域关键词
TECH_KEYWORDS = [
    "technology",
    "tech company",
    "semiconductor",
    "chip",
    "chips",
    "gpu",
    "processor",
    "robotics",
    "robot",
    "cloud computing",
    "cybersecurity",
    "software",
    "hardware",
    "data center",
    "apple",
    "google",
    "microsoft",
    "meta",
    "amazon",
    "nvidia",
    "tesla",
    "芯片",
    "半导体",
    "处理器",
    "机器人",
    "云计算",
    "网络安全",
    "软件",
    "硬件",
    "数据中心",
    "科技",
    "智能手机",
    "操作系统",
]

# 财经领域关键词
FINANCE_KEYWORDS = [
    "funding",
    "raises",
    "raised",
    "investment",
    "investor",
    "ipo",
    "acquisition",
    "acquires",
    "merger",
    "valuation",
    "revenue",
    "earnings",
    "profit",
    "stock",
    "shares",
    "market cap",
    "venture capital",
    "融资",
    "投资",
    "上市",
    "收购",
    "并购",
    "估值",
    "营收",
    "财报",
    "利润",
    "股价",
    "股票",
    "风险投资",
]


def classify_news(news: dict) -> list[str]:
    """
    根据新闻标题和摘要识别所属领域。
    一篇新闻可以同时属于多个领域。
    """

    text = (str(news.get("title") or "") + " " + str(news.get("summary") or "")).lower()

    categories = []

    if any(keyword.lower() in text for keyword in AI_KEYWORDS):
        categories.append("AI")

    if any(keyword.lower() in text for keyword in TECH_KEYWORDS):
        categories.append("科技")

    if any(keyword.lower() in text for keyword in FINANCE_KEYWORDS):
        categories.append("财经")

    return categories


def filter_news(news_list: list[dict]) -> list[dict]:
    """
    过滤不属于 AI、科技、财经领域的新闻，
    并为相关新闻添加 categories 字段。
    """

    result = []

    for news in news_list:
        categories = classify_news(news)

        # 没有识别出任何目标领域，跳过
        if not categories:
            continue

        # 保留原始新闻信息，增加分类结果
        news["categories"] = categories

        result.append(news)

    return result


news_list = [
    {
        "title": "OpenAI launches a new AI model",
        "summary": "A new large language model."
    },
    {
        "title": "NVIDIA announces new GPU chips",
        "summary": "New chips designed for AI computing."
    },
    {
        "title": "Payhawk raises $280M in funding",
        "summary": "The company reaches a $2 billion valuation."
    },
    {
        "title": "GTA 6 release date announced",
        "summary": "The latest video game release news."
    }
]

result = filter_news(news_list)

for news in result:
    print(news["title"], news["categories"])