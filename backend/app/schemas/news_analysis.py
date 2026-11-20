"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 17:20:14
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 17:24:26
"""

from pydantic import BaseModel, Field


class NewsAnalysis(BaseModel):
    category: str = Field(..., description="新闻类别")
    score: int = Field(..., ge=0, le=100, description="新闻价值评分，范围 0～100")
    importance: str = Field(..., description="重要程度")
    companies: list[str] = Field(..., description="涉及公司")
    technologies: list[str] = Field(..., description="涉及技术")
    event_summary: str = Field(..., description="事件摘要")
    industry_impact: str = Field(..., description="行业影响")
    reason: str = Field(..., description="评分理由")


if __name__ == "__main__":
    result = NewsAnalysis(
        category="AI模型",
        score=92,
        importance="high",
        companies=["Anthropic"],
        technologies=["LLM", "Claude"],
        event_summary="Anthropic 发布了新的模型能力。",
        industry_impact="推动企业级 AI Agent 应用发展。",
        reason="涉及核心模型能力更新，具有较高行业价值。",
    )

    print(result)
    print(result.model_dump())
