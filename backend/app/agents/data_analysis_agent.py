"""数据分析Agent - 负责数据分析和可视化"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent


class DataAnalysisAgent(BaseAgent):
    """数据分析Agent，负责数据分析、统计和洞察"""
    
    def __init__(self):
        super().__init__(
            name="DataAnalysisAgent",
            description="负责数据分析、统计计算、趋势分析和数据洞察"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据分析任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._analyze_data(user_input, parameters)
    
    async def _analyze_data(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """分析数据"""
        system_prompt = """你是一个数据分析专家。根据用户提供的数据或需求进行分析。

返回格式：
{
    "analysis_type": "分析类型",
    "findings": [
        {
            "insight": "发现的洞察",
            "importance": "high/medium/low",
            "explanation": "详细解释"
        }
    ],
    "statistics": {
        "key_metrics": "关键指标"
    },
    "recommendations": ["建议1", "建议2"],
    "visualization_suggestion": "可视化建议"
}"""

        prompt = f"数据/需求：{user_input}\n\n请进行数据分析（JSON格式）。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            analysis = json.loads(response)
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "数据分析完成"
            }
        except Exception as e:
            return {"success": False, "error": f"数据分析失败: {str(e)}"}
