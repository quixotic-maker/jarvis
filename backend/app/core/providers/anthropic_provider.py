"""
Anthropic Provider实现
支持Claude-3系列模型
"""
import anthropic
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.core.llm_provider import LLMProvider, ChatRequest, ChatResponse, Message, UsageStats
from app.core.llm_config import ModelConfig, LLMProviderType


class AnthropicProvider(LLMProvider):
    """Anthropic Provider实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.default_model = config.get("model", "claude-3-sonnet-20240229")
        self.timeout = config.get("timeout", 60)
        
        if not self.api_key:
            raise ValueError("Anthropic API key未配置")
        
        # 配置Anthropic客户端
        client_kwargs = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        self.client = anthropic.AsyncAnthropic(**client_kwargs)
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """非流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # Anthropic需要分离system消息
        system_messages = [msg.content for msg in request.messages if msg.role == "system"]
        system = "\n".join(system_messages) if system_messages else None
        
        # 其他消息
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
            if msg.role != "system"
        ]
        
        try:
            response = await self.client.messages.create(
                model=model,
                messages=messages,
                system=system,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            content = response.content[0].text
            usage = response.usage
            
            # 计算成本
            cost = await self.calculate_cost(
                usage.input_tokens,
                usage.output_tokens,
                model
            )
            
            # 记录使用统计
            await self.record_usage(UsageStats(
                provider=LLMProviderType.ANTHROPIC,
                model=model,
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens,
                total_tokens=usage.input_tokens + usage.output_tokens,
                cost=cost
            ))
            
            return ChatResponse(
                content=content,
                model=model,
                usage={
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens
                },
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API调用失败: {str(e)}")
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # 分离system消息
        system_messages = [msg.content for msg in request.messages if msg.role == "system"]
        system = "\n".join(system_messages) if system_messages else None
        
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
            if msg.role != "system"
        ]
        
        try:
            full_content = ""
            prompt_tokens = 0
            completion_tokens = 0
            
            async with self.client.messages.stream(
                model=model,
                messages=messages,
                system=system,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ) as stream:
                async for text in stream.text_stream:
                    full_content += text
                    yield text
                
                # 获取最终消息以获取token使用情况
                final_message = await stream.get_final_message()
                prompt_tokens = final_message.usage.input_tokens
                completion_tokens = final_message.usage.output_tokens
            
            # 记录使用统计
            cost = await self.calculate_cost(prompt_tokens, completion_tokens, model)
            
            await self.record_usage(UsageStats(
                provider=LLMProviderType.ANTHROPIC,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost=cost
            ))
            
        except Exception as e:
            raise RuntimeError(f"Anthropic Stream API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        计算token数量
        Anthropic的token计数需要API调用，这里使用近似方法
        通常1个token约等于4个字符
        """
        # 简化计算：英文约4字符/token，中文约2字符/token
        # 这只是近似值
        return len(text) // 3
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    async def calculate_cost(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str
    ) -> float:
        """计算成本"""
        pricing = ModelConfig.get_pricing(LLMProviderType.ANTHROPIC, model)
        
        # 价格是每1000 tokens
        prompt_cost = (prompt_tokens / 1000) * pricing["input"]
        completion_cost = (completion_tokens / 1000) * pricing["output"]
        
        return prompt_cost + completion_cost
