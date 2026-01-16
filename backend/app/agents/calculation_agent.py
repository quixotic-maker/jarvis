"""计算Agent - 负责数学计算和数据分析"""
from typing import Dict, Any
import json
import re

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service
from app.core.cot_prompts import CoTPattern


class CalculationAgent(BaseAgent):
    """计算Agent，负责数学计算、数据分析和统计"""
    
    def __init__(self):
        super().__init__(
            name="CalculationAgent",
            description="负责数学计算、数据分析、统计和公式求解"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行计算任务
        
        Args:
            input_data: {
                "user_input": "用户输入",
                "parameters": {}
            }
        """
        user_input = input_data.get("user_input", "")
        
        return await self._calculate(user_input)
    
    async def _calculate(self, user_input: str) -> Dict[str, Any]:
        """执行计算（集成Prompt系统，使用CoT）"""
        
        # 使用Prompt系统，带CoT示例
        messages = prompt_service.build_messages(
            agent_name="calculation_agent",
            user_input=user_input,
            use_few_shot=True,
            num_examples=1,
            use_cot=True,
            cot_pattern=CoTPattern.STEP_BY_STEP,
            output_format="{\"expression\": \"...\", \"result\": ..., \"steps\": [...], \"explanation\": \"...\"}"
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else user_input
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
            
            # 清理JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            calc_data = json.loads(response)
            
            return {
                "success": True,
                "calculation": calc_data,
                "message": "计算完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"计算失败: {str(e)}"
            }
