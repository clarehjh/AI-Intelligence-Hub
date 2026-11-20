"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-20 17:09:07
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 17:36:48
"""

"""
Description:
version:
Author: Huangjiahui
Date: 2026-11-18 19:31:44
LastEditors: Huangjiahui
LastEditTime: 2026-11-20 17:31:45
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Intelligence Hub"
    APP_ENV: str = "development"

    LLM_PROVIDER: str = "qwen"
    LLM_MODEL: str = "qwen3.7-flash"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_API_KEY: str = ""

    DATABASE_URL: str = "sqlite:///./data/ai_hub.db"
    # 表示从项目运行目录下的 .env 文件读取配置，编码使用 UTF-8，并忽略未声明的额外配置项。
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
