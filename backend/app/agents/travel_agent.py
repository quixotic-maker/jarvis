"""旅行Agent - 负责旅行规划"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service


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
        """规划旅行（集成Prompt系统）"""
        
        # 使用Prompt系统
        messages = prompt_service.build_messages(
            agent_name="travel_agent",
            user_input=user_input,
            use_few_shot=False,
            output_format="{\"destination\": \"...\", \"duration\": \"...\", \"itinerary\": [...], \"budget\": \"...\", \"tips\": [...], \"packing_list\": [...]}"
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else user_input
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
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
