"""基础Agent类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.db.models import AgentLog


class BaseAgent(ABC):
    """所有Agent的基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        pass
    
    async def process_with_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        使用LLM处理提示
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Returns:
            LLM响应
        """
        # 根据配置选择LLM提供商
        if settings.DEFAULT_LLM_PROVIDER == "deepseek":
            return await self._call_deepseek(prompt, system_prompt)
        elif settings.DEFAULT_LLM_PROVIDER == "openai":
            return await self._call_openai(prompt, system_prompt)
        elif settings.DEFAULT_LLM_PROVIDER == "anthropic":
            return await self._call_anthropic(prompt, system_prompt)
        else:
            raise ValueError(f"不支持的LLM提供商: {settings.DEFAULT_LLM_PROVIDER}")
    
    async def _call_deepseek(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用DeepSeek API"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=settings.DEFAULT_MODEL,  # deepseek-chat
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用OpenAI API"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用Anthropic API"""
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            system=system_prompt if system_prompt else "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def log_execution(
        self,
        db,
        task_id: Optional[int],
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time: int,
        status: str,
        error_message: Optional[str] = None
    ):
        """记录Agent执行日志"""
        log = AgentLog(
            agent_name=self.name,
            task_id=task_id,
            action=action,
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time,
            status=status,
            error_message=error_message
        )
        db.add(log)
        db.commit()
