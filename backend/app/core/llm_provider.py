"""
LLM Provider抽象基类
定义统一的LLM接口，支持多个提供商
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    """消息模型"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


class ChatRequest(BaseModel):
    """对话请求"""
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应"""
    content: str
    model: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str
    created_at: datetime = datetime.now()


class UsageStats(BaseModel):
    """使用统计"""
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float  # USD
    created_at: datetime = datetime.now()


class LLMProvider(ABC):
    """LLM Provider抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Provider
        
        Args:
            config: Provider配置字典
        """
        self.config = config
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        非流式对话
        
        Args:
            request: 对话请求
            
        Returns:
            对话响应
        """
        pass
    
    @abstractmethod
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        流式对话
        
        Args:
            request: 对话请求
            
        Yields:
            生成的文本片段
        """
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        计算token数量
        
        Args:
            text: 文本内容
            model: 模型名称
            
        Returns:
            token数量
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型名称列表
        """
        pass
    
    async def calculate_cost(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str
    ) -> float:
        """
        计算成本
        
        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            model: 模型名称
            
        Returns:
            成本（USD）
        """
        # 子类可以覆盖此方法实现自定义计价
        return 0.0
    
    async def record_usage(self, usage: UsageStats) -> None:
        """
        记录使用统计
        
        Args:
            usage: 使用统计数据
        """
        # 子类可以覆盖此方法实现自定义统计记录
        pass
    
    def validate_request(self, request: ChatRequest) -> None:
        """
        验证请求参数
        
        Args:
            request: 对话请求
            
        Raises:
            ValueError: 参数不合法时抛出
        """
        if not request.messages:
            raise ValueError("messages不能为空")
        
        if request.temperature < 0 or request.temperature > 2:
            raise ValueError("temperature必须在0-2之间")
        
        if request.max_tokens < 1:
            raise ValueError("max_tokens必须大于0")
