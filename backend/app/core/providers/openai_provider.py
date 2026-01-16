"""
OpenAI Provider实现
支持GPT-3.5和GPT-4系列模型
"""
import openai
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.core.llm_provider import LLMProvider, ChatRequest, ChatResponse, Message, UsageStats
from app.core.llm_config import ModelConfig, LLMProviderType
import tiktoken
from datetime import datetime


class OpenAIProvider(LLMProvider):
    """OpenAI Provider实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.default_model = config.get("model", "gpt-3.5-turbo")
        self.timeout = config.get("timeout", 60)
        
        if not self.api_key:
            raise ValueError("OpenAI API key未配置")
        
        # 配置OpenAI客户端
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """非流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            
            choice = response.choices[0]
            usage = response.usage
            
            # 计算成本
            cost = await self.calculate_cost(
                usage.prompt_tokens,
                usage.completion_tokens,
                model
            )
            
            # 记录使用统计
            await self.record_usage(UsageStats(
                provider=LLMProviderType.OPENAI,
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost
            ))
            
            return ChatResponse(
                content=choice.message.content,
                model=model,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                finish_reason=choice.finish_reason
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            full_content = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content
            
            # 流式完成后估算token使用（简化处理）
            prompt_tokens = await self.count_tokens(
                " ".join([msg.content for msg in request.messages]),
                model
            )
            completion_tokens = await self.count_tokens(full_content, model)
            
            cost = await self.calculate_cost(prompt_tokens, completion_tokens, model)
            
            await self.record_usage(UsageStats(
                provider=LLMProviderType.OPENAI,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost=cost
            ))
            
        except Exception as e:
            raise RuntimeError(f"OpenAI Stream API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """计算token数量"""
        model = model or self.default_model
        
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 如果模型不支持，使用默认编码
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    async def calculate_cost(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str
    ) -> float:
        """计算成本"""
        pricing = ModelConfig.get_pricing(LLMProviderType.OPENAI, model)
        
        # 价格是每1000 tokens
        prompt_cost = (prompt_tokens / 1000) * pricing["input"]
        completion_cost = (completion_tokens / 1000) * pricing["output"]
        
        return prompt_cost + completion_cost
