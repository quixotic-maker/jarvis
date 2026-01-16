"""
LLM Provider配置管理
支持多个LLM提供商的统一配置
"""
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from enum import Enum


class LLMProviderType(str, Enum):
    """LLM提供商类型"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfig(BaseSettings):
    """LLM统一配置"""
    
    # 默认提供商
    default_provider: LLMProviderType = LLMProviderType.OPENAI
    
    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Anthropic配置
    anthropic_api_key: Optional[str] = None
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-3-sonnet-20240229"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 2000
    
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ollama_temperature: float = 0.7
    
    # 通用配置
    timeout: int = 60  # 请求超时（秒）
    max_retries: int = 3  # 最大重试次数
    
    # 限流配置
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    
    # 成本统计
    cost_tracking_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ModelConfig:
    """模型配置数据类"""
    
    # OpenAI模型价格（每1000 tokens，USD）
    OPENAI_PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    # Anthropic模型价格
    ANTHROPIC_PRICING = {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    }
    
    # 模型上下文长度
    CONTEXT_LENGTHS = {
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-3.5-turbo": 16385,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
    }
    
    @classmethod
    def get_pricing(cls, provider: LLMProviderType, model: str) -> Dict[str, float]:
        """获取模型定价"""
        if provider == LLMProviderType.OPENAI:
            return cls.OPENAI_PRICING.get(model, {"input": 0, "output": 0})
        elif provider == LLMProviderType.ANTHROPIC:
            return cls.ANTHROPIC_PRICING.get(model, {"input": 0, "output": 0})
        return {"input": 0, "output": 0}
    
    @classmethod
    def get_context_length(cls, model: str) -> int:
        """获取模型上下文长度"""
        return cls.CONTEXT_LENGTHS.get(model, 4096)


# 全局配置实例
llm_config = LLMConfig()
