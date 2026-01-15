"""应用配置"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # ========== 基础配置 ==========
    APP_NAME: str = "Jarvis"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ========== 数据库配置 ==========
    DATABASE_URL: str = "sqlite:///./jarvis.db"
    
    # ========== LLM配置 ==========
    # DeepSeek（推荐）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    # OpenAI（备用）
    OPENAI_API_KEY: str = ""
    
    # Anthropic（备用）
    ANTHROPIC_API_KEY: str = ""
    
    # 默认LLM设置
    DEFAULT_LLM_PROVIDER: str = "deepseek"  # deepseek, openai, anthropic
    DEFAULT_MODEL: str = "deepseek-chat"  # deepseek-chat, deepseek-coder, gpt-4-turbo-preview
    
    # ========== Redis配置 ==========
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # 设为True启用Redis
    
    # ========== Celery任务队列配置 ==========
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ========== CORS配置 ==========
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:5173"
    ]
    
    # ========== 安全配置 ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # ========== 天气API配置 ==========
    # 和风天气 (https://dev.qweather.com/)
    QWEATHER_API_KEY: str = ""  # 和风天气API Key
    QWEATHER_BASE_URL: str = "https://devapi.qweather.com/v7"
    
    # ========== 新闻API配置 ==========
    # NewsAPI (https://newsapi.org/)
    NEWS_API_KEY: str = ""
    
    # ========== 地图API配置 ==========
    # 高德地图 (https://lbs.amap.com/)
    AMAP_API_KEY: str = ""  # 高德地图Web API Key
    
    # ========== 翻译API配置 ==========
    # 百度翻译 (https://fanyi-api.baidu.com/)
    BAIDU_TRANSLATE_APPID: str = ""
    BAIDU_TRANSLATE_SECRET: str = ""
    
    # ========== 股票/财经API ==========
    # 东方财富
    EASTMONEY_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
