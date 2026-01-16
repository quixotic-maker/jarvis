"""健康Agent - 负责健康管理"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service


class HealthAgent(BaseAgent):
    """健康Agent，负责健康建议和管理"""
    
    def __init__(self):
        super().__init__(
            name="HealthAgent",
            description="负责健康建议、运动计划、饮食建议和健康跟踪"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行健康管理任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        action = parameters.get("action", "advice")
        
        if action == "advice":
            return await self._health_advice(user_input)
        elif action == "workout":
            return await self._workout_plan(user_input)
        elif action == "diet":
            return await self._diet_plan(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _health_advice(self, user_input: str) -> Dict[str, Any]:
        """健康建议（集成Prompt系统）"""
        
        # 使用Prompt系统
        messages = prompt_service.build_messages(
            agent_name="health_agent",
            user_input=user_input,
            use_few_shot=False,
            constraints=["科学健康建议", "说明不能替代医疗", "严重问题建议就医"]
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else user_input
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
            
            return {
                "success": True,
                "advice": response,
                "disclaimer": "本建议仅供参考，不能替代专业医疗意见",
                "message": "健康建议已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成建议失败: {str(e)}"}
    
    async def _workout_plan(self, user_input: str) -> Dict[str, Any]:
        """运动计划"""
        system_prompt = """你是一个健身教练。制定科学的运动计划。

返回格式：
{
    "goal": "健身目标",
    "level": "初级/中级/高级",
    "weekly_plan": [
        {
            "day": "周一",
            "exercises": [
                {"name": "运动名称", "sets": 3, "reps": 15, "duration": "30分钟"}
            ]
        }
    ],
    "tips": ["注意事项1", "注意事项2"]
}"""

        prompt = f"用户需求：{user_input}\n\n请制定运动计划（JSON格式）。"
        
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
            
            workout = json.loads(response)
            
            return {
                "success": True,
                "workout_plan": workout,
                "message": "运动计划已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成运动计划失败: {str(e)}"}
    
    async def _diet_plan(self, user_input: str) -> Dict[str, Any]:
        """饮食计划"""
        system_prompt = """你是一个营养师。制定健康的饮食计划。

返回格式：
{
    "goal": "饮食目标",
    "daily_calories": 2000,
    "meal_plan": [
        {
            "meal": "早餐/午餐/晚餐",
            "foods": ["食物1", "食物2"],
            "calories": 500,
            "nutrients": "营养说明"
        }
    ],
    "tips": ["饮食建议1", "饮食建议2"]
}"""

        prompt = f"用户需求：{user_input}\n\n请制定饮食计划（JSON格式）。"
        
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
            
            diet = json.loads(response)
            
            return {
                "success": True,
                "diet_plan": diet,
                "message": "饮食计划已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成饮食计划失败: {str(e)}"}
