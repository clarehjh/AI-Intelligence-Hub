import time

from openai import (
    OpenAI,
    RateLimitError,
    AuthenticationError,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)
from app.config import settings
from app.schemas.news_analysis import NewsAnalysis
client = OpenAI(
    api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL, max_retries=0
)


def analyze_news(title: str, summary: str = "", content: str = "") -> NewsAnalysis:

    

    system_prompt = """
    你是一名专业的 AI 行业新闻分析师。

    【最重要的输出规则】
    所有面向用户的分析内容必须使用简体中文。
    即使输入新闻是英文，也必须使用简体中文分析。
    禁止使用英文句子回答。

    【字段要求】
    1. category：新闻类别，必须使用简体中文。
      例如：AI模型、企业应用、融资并购、AI安全。

    2. score：新闻价值评分，0到100之间的整数。

    3. importance：只能是 high、medium、low。

    4. companies：涉及的公司名称。
      保留官方英文名称，例如 Anthropic、OpenAI。

    5. technologies：涉及的技术。
      使用简体中文，必要时保留英文专有名词。
      例如：大语言模型（LLM）、检索增强生成（RAG）。

    6. event_summary：必须使用简体中文描述新闻事件。

    7. industry_impact：必须使用简体中文分析行业影响。

    8. reason：必须使用简体中文解释评分理由。

    【输出要求】
    只返回符合 JSON 格式的数据。
    不要返回 Markdown。
    不要返回 JSON 以外的解释。
    """

    user_prompt = f"""
    请分析以下新闻：

    新闻标题：{title}
    新闻摘要：{summary}
    新闻正文：{content}
    """


    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                timeout=30,
                temperature=0
            )
            break

        except RateLimitError:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** (attempt + 1)
            print(f"请求被限流，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

        except (APITimeoutError, APIConnectionError):
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** (attempt + 1)
            print(f"网络或请求超时，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

        except AuthenticationError:
            print("API Key 认证失败，请检查配置")
            raise

        except APIStatusError as e:
            print(f"模型服务返回错误，状态码：{e.status_code}")
            raise

    result = response.choices[0].message.content

    if not result:
        raise ValueError("模型没有返回有效内容")

    return NewsAnalysis.model_validate_json(result)


if __name__ == "__main__":
    result = analyze_news(
        title="Anthropic announces new AI model capabilities",
        summary="Anthropic announced new capabilities for its AI models.",
        content="The update aims to improve enterprise AI applications and agent development.",
    )

    print("新闻分析结果：")
    print(result.model_dump_json(indent=2))
