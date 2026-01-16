"""
Ollama Provider实现
支持本地部署的开源模型
"""
import httpx
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.core.llm_provider import LLMProvider, ChatRequest, ChatResponse, Message, UsageStats
from app.core.llm_config import LLMProviderType


class OllamaProvider(LLMProvider):
    """Ollama Provider实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.default_model = config.get("model", "llama2")
        self.timeout = config.get("timeout", 120)  # Ollama可能需要更长时间
        
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """非流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # 转换消息格式
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                }
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("message", {}).get("content", "")
            
            # Ollama不返回准确的token数，使用近似值
            prompt_tokens = await self.count_tokens(
                " ".join([msg.content for msg in request.messages]),
                model
            )
            completion_tokens = await self.count_tokens(content, model)
            
            # Ollama是免费的，成本为0
            await self.record_usage(UsageStats(
                provider=LLMProviderType.OLLAMA,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost=0.0
            ))
            
            return ChatResponse(
                content=content,
                model=model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                finish_reason="stop"
            )
            
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama API调用失败: {str(e)}")
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """流式对话"""
        self.validate_request(request)
        
        model = request.model or self.default_model
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        try:
            full_content = ""
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                full_content += content
                                yield content
                        except json.JSONDecodeError:
                            continue
            
            # 记录使用统计
            prompt_tokens = await self.count_tokens(
                " ".join([msg.content for msg in request.messages]),
                model
            )
            completion_tokens = await self.count_tokens(full_content, model)
            
            await self.record_usage(UsageStats(
                provider=LLMProviderType.OLLAMA,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost=0.0
            ))
            
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama Stream API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        计算token数量
        Ollama没有内置token计数，使用近似方法
        """
        # 简化计算：平均每个token约3-4个字符
        return len(text) // 3
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        # 这里返回常见的Ollama模型
        # 实际可以通过API查询：GET /api/tags
        return [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "mistral",
            "mixtral",
            "codellama",
            "phi",
            "qwen"
        ]
    
    async def calculate_cost(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str
    ) -> float:
        """
        计算成本
        Ollama是本地运行，没有API费用
        """
        return 0.0
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
