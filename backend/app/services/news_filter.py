
# AI 情报关注关键词
AI_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "artificial intelligence",
    "agent",
    "agents",
    "LLM",
    "large language model",
    "OpenAI",
    "Anthropic",
    "ChatGPT",
    "Claude",
    "Gemini",
    "RAG",
    "MCP",
    "LangChain",
    "LangGraph",
    "DeepSeek",
    "Nvidia",
]

def filter_news(news_list: list[dict], limit: int = 15) -> list[dict]:
    """
    根据新闻标题和摘要筛选 AI 相关新闻。
    """

    result = []

    for news in news_list:
        text = (
            news.get("title", "") + " " +
            news.get("summary", "")
        ).lower()

        if any(keyword.lower() in text for keyword in AI_KEYWORDS):
            result.append(news)

    return result[:limit]
