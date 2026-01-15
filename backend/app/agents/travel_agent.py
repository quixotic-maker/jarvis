"""旅行Agent - 负责旅行规划"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent


class TravelAgent(BaseAgent):
    """旅行Agent，负责旅行规划和建议"""
    
    def __init__(self):
        super().__init__(
            name="TravelAgent",
            description="负责旅行规划、行程安排、景点推荐和旅行建议"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行旅行规划任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._plan_trip(user_input, parameters)
    
    async def _plan_trip(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """规划旅行"""
        system_prompt = """你是一个专业的旅行规划师。根据用户需求制定详细的旅行计划。

返回格式：
{
    "destination": "目的地",
    "duration": "建议天数",
    "itinerary": [
        {
            "day": 1,
            "activities": ["活动1", "活动2"],
            "attractions": ["景点1", "景点2"],
            "meals": "餐饮建议",
            "accommodation": "住宿建议"
        }
    ],
    "budget": "预算建议",
    "tips": ["旅行建议1", "旅行建议2"],
    "packing_list": ["物品1", "物品2"]
}"""

        prompt = f"用户需求：{user_input}\n\n请制定旅行计划（JSON格式）。"
        
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
            
            trip_plan = json.loads(response)
            
            return {
                "success": True,
                "trip_plan": trip_plan,
                "message": "旅行计划已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成旅行计划失败: {str(e)}"}
