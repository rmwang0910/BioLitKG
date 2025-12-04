"""
独立的配置管理系统
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class LLMConfig(BaseSettings):
    """LLM配置"""
    
    api_key: str = Field(
        default="",
        description="API密钥",
        validation_alias="LLM_API_KEY"
    )
    
    base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="API base URL",
        validation_alias="LLM_BASE_URL"
    )
    
    model: str = Field(
        default="qwen-plus",
        description="模型名称",
        validation_alias="LLM_MODEL"
    )
    
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.7)
    timeout: int = Field(default=120)
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class LiteratureConfig(BaseSettings):
    """文献搜索配置"""
    
    search_timeout: int = Field(default=120)
    max_results_per_query: int = Field(default=100)
    api_timeout: int = Field(default=30)
    pdf_download_timeout: int = Field(default=60)
    cache_enabled: bool = Field(default=False)
    semantic_scholar_api_key: Optional[str] = Field(default=None)
    pubmed_api_key: Optional[str] = Field(default=None)
    pubmed_email: Optional[str] = Field(default="biolit@example.com")
    
    class Config:
        env_prefix = "LIT_"


class AppConfig:
    """应用配置"""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.literature = LiteratureConfig()


_config: Optional[AppConfig] = None


def get_config(reload: bool = False) -> AppConfig:
    """获取配置"""
    global _config
    if _config is None or reload:
        _config = AppConfig()
    return _config

