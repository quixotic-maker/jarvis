"""推荐Agent - 负责个性化推荐"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service


class RecommendationAgent(BaseAgent):
    """推荐Agent，负责个性化推荐和建议"""
    
    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            description="负责电影、书籍、音乐、餐厅等个性化推荐"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行推荐任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._recommend(user_input, parameters)
    
    async def _recommend(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """生成推荐（集成Prompt系统）"""
        category = parameters.get("category", "通用")
        
        # 使用Prompt系统
        messages = prompt_service.build_messages(
            agent_name="recommendation_agent",
            user_input=user_input,
            use_few_shot=False,
            context=f"推荐类别：{category}",
            output_format="{\"category\": \"...\", \"recommendations\": [{\"title\": \"...\", \"description\": \"...\", \"reason\": \"...\", \"rating\": 4.5, \"tags\": [...]}], \"total\": 5}"
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
            
            recommendations = json.loads(response)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "message": "推荐已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成推荐失败: {str(e)}"}
