"""
LLM API端点
提供统一的LLM调用接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.llm_factory import get_provider
from app.core.llm_config import LLMProviderType
from app.core.llm_provider import ChatRequest, Message
from app.api.schemas import BaseResponse, ResponseStatus
import json


router = APIRouter()


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    """聊天补全请求"""
    messages: List[ChatMessage]
    model: Optional[str] = None
    provider: Optional[str] = None  # openai/anthropic/ollama
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


@router.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """
    创建聊天补全
    支持多个LLM provider和流式/非流式响应
    """
    try:
        # 确定provider类型
        provider_type = None
        if request.provider:
            provider_map = {
                "openai": LLMProviderType.OPENAI,
                "anthropic": LLMProviderType.ANTHROPIC,
                "ollama": LLMProviderType.OLLAMA,
            }
            provider_type = provider_map.get(request.provider.lower())
            if not provider_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的provider: {request.provider}"
                )
        
        # 获取provider实例
        provider = get_provider(provider_type)
        
        # 转换消息格式
        messages = [
            Message(role=msg.role, content=msg.content)
            for msg in request.messages
        ]
        
        # 创建ChatRequest
        chat_request = ChatRequest(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # 流式响应
        if request.stream:
            async def generate():
                try:
                    async for chunk in provider.chat_stream(chat_request):
                        # SSE格式
                        data = {"content": chunk}
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    error_data = {"error": str(e)}
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        
        # 非流式响应
        response = await provider.chat(chat_request)
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="聊天补全成功",
            data=ChatCompletionResponse(
                content=response.content,
                model=response.model,
                usage=response.usage,
                finish_reason=response.finish_reason
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/models")
async def list_models(provider: Optional[str] = None):
    """
    获取可用模型列表
    """
    try:
        # 确定provider类型
        provider_type = None
        if provider:
            provider_map = {
                "openai": LLMProviderType.OPENAI,
                "anthropic": LLMProviderType.ANTHROPIC,
                "ollama": LLMProviderType.OLLAMA,
            }
            provider_type = provider_map.get(provider.lower())
        
        # 获取provider实例
        llm_provider = get_provider(provider_type)
        models = llm_provider.get_available_models()
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="获取模型列表成功",
            data={
                "provider": provider or "default",
                "models": models
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/providers")
async def list_providers():
    """
    获取可用的LLM providers
    """
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="获取provider列表成功",
        data={
            "providers": [
                {
                    "name": "openai",
                    "display_name": "OpenAI",
                    "description": "OpenAI GPT系列模型",
                    "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
                },
                {
                    "name": "anthropic",
                    "display_name": "Anthropic",
                    "description": "Anthropic Claude系列模型",
                    "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
                },
                {
                    "name": "ollama",
                    "display_name": "Ollama",
                    "description": "本地开源模型",
                    "supported_models": ["llama2", "mistral", "mixtral", "codellama"]
                }
            ]
        }
    )


@router.post("/count-tokens")
async def count_tokens(
    text: str,
    model: Optional[str] = None,
    provider: Optional[str] = None
):
    """
    计算文本的token数量
    """
    try:
        # 确定provider类型
        provider_type = None
        if provider:
            provider_map = {
                "openai": LLMProviderType.OPENAI,
                "anthropic": LLMProviderType.ANTHROPIC,
                "ollama": LLMProviderType.OLLAMA,
            }
            provider_type = provider_map.get(provider.lower())
        
        # 获取provider实例
        llm_provider = get_provider(provider_type)
        token_count = await llm_provider.count_tokens(text, model)
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Token计数成功",
            data={
                "text_length": len(text),
                "token_count": token_count,
                "model": model or "default"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
