"""翻译Agent - 负责多语言翻译"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent


class TranslationAgent(BaseAgent):
    """翻译Agent，负责多语言翻译和语言检测"""
    
    def __init__(self):
        super().__init__(
            name="TranslationAgent",
            description="负责多语言翻译、语言检测和本地化"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行翻译任务
        
        Args:
            input_data: {
                "user_input": "用户输入",
                "parameters": {"target_lang": "目标语言"}
            }
        """
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._translate(user_input, parameters)
    
    async def _translate(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """执行翻译"""
        target_lang = parameters.get("target_lang", "English")
        
        system_prompt = f"""你是一个专业的翻译助手。请将用户的文本翻译成{target_lang}。

返回格式：
{{
    "original": "原文",
    "translated": "译文",
    "source_lang": "源语言",
    "target_lang": "{target_lang}",
    "confidence": 0.95
}}

提供准确、地道的翻译。"""

        prompt = f"请翻译以下文本：\n{user_input}\n\n返回JSON格式。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            # 清理JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            translation_data = json.loads(response)
            
            return {
                "success": True,
                "translation": translation_data,
                "message": "翻译完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"翻译失败: {str(e)}"
            }
