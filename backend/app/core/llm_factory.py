"""
LLM Provider Factory
动态创建和管理LLM Provider实例
"""
from typing import Dict, Any, Optional
from app.core.llm_config import LLMProviderType, llm_config
from app.core.llm_provider import LLMProvider
from app.core.providers import OpenAIProvider, AnthropicProvider, OllamaProvider


class ProviderFactory:
    """Provider工厂类"""
    
    # Provider类映射
    _providers = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
        LLMProviderType.OLLAMA: OllamaProvider,
    }
    
    # Provider实例缓存（单例模式）
    _instances: Dict[LLMProviderType, LLMProvider] = {}
    
    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[LLMProviderType] = None,
        config_override: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        """
        获取Provider实例
        
        Args:
            provider_type: Provider类型，默认使用配置的默认provider
            config_override: 配置覆盖，用于自定义配置
        
        Returns:
            LLMProvider实例
        """
        # 使用默认provider
        if provider_type is None:
            provider_type = llm_config.default_provider
        
        # 如果没有配置覆盖且已有实例，返回缓存的实例
        if config_override is None and provider_type in cls._instances:
            return cls._instances[provider_type]
        
        # 获取Provider类
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"不支持的Provider类型: {provider_type}")
        
        # 构建配置
        config = cls._build_config(provider_type, config_override)
        
        # 创建实例
        instance = provider_class(config)
        
        # 缓存实例（仅当没有配置覆盖时）
        if config_override is None:
            cls._instances[provider_type] = instance
        
        return instance
    
    @classmethod
    def _build_config(
        cls,
        provider_type: LLMProviderType,
        config_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构建Provider配置
        
        Args:
            provider_type: Provider类型
            config_override: 配置覆盖
        
        Returns:
            配置字典
        """
        config = {
            "timeout": llm_config.timeout,
            "max_retries": llm_config.max_retries,
        }
        
        if provider_type == LLMProviderType.OPENAI:
            # 如果配置了DeepSeek，优先使用DeepSeek配置
            if llm_config.deepseek_api_key:
                config.update({
                    "api_key": llm_config.deepseek_api_key,
                    "base_url": llm_config.deepseek_base_url,
                    "model": llm_config.deepseek_model,
                })
            else:
                config.update({
                    "api_key": llm_config.openai_api_key,
                    "base_url": llm_config.openai_base_url,
                    "model": llm_config.openai_model,
                })
        elif provider_type == LLMProviderType.ANTHROPIC:
            config.update({
                "api_key": llm_config.anthropic_api_key,
                "base_url": llm_config.anthropic_base_url,
                "model": llm_config.anthropic_model,
            })
        elif provider_type == LLMProviderType.OLLAMA:
            config.update({
                "base_url": llm_config.ollama_base_url,
                "model": llm_config.ollama_model,
            })
        
        # 应用配置覆盖
        if config_override:
            config.update(config_override)
        
        return config
    
    @classmethod
    def create_custom_provider(
        cls,
        provider_class: type,
        config: Dict[str, Any]
    ) -> LLMProvider:
        """
        创建自定义Provider
        
        Args:
            provider_class: Provider类
            config: 配置
        
        Returns:
            LLMProvider实例
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError("provider_class必须是LLMProvider的子类")
        
        return provider_class(config)
    
    @classmethod
    def clear_cache(cls):
        """清除实例缓存"""
        cls._instances.clear()


# 便捷函数
def get_provider(
    provider_type: Optional[LLMProviderType] = None,
    config_override: Optional[Dict[str, Any]] = None
) -> LLMProvider:
    """
    获取Provider实例（便捷函数）
    
    Args:
        provider_type: Provider类型
        config_override: 配置覆盖
    
    Returns:
        LLMProvider实例
    """
    return ProviderFactory.get_provider(provider_type, config_override)
