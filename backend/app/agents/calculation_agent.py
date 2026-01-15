"""计算Agent - 负责数学计算和数据分析"""
from typing import Dict, Any
import json
import re

from app.agents.base_agent import BaseAgent


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
        """执行计算"""
        system_prompt = """你是一个数学和计算助手。根据用户的问题进行计算并解释。

返回格式：
{
    "expression": "计算表达式",
    "result": 计算结果,
    "steps": ["步骤1", "步骤2"],
    "explanation": "结果解释"
}

支持：基本运算、代数、统计、百分比、单位转换等。"""

        prompt = f"用户问题：{user_input}\n\n请进行计算并返回JSON格式结果。"
        
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
