"""推荐Agent - 负责个性化推荐"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent


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
        """生成推荐"""
        category = parameters.get("category", "通用")
        
        system_prompt = f"""你是一个{category}推荐专家。根据用户的喜好和需求提供个性化推荐。

返回格式：
{{
    "category": "{category}",
    "recommendations": [
        {{
            "title": "推荐项目名称",
            "description": "简介",
            "reason": "推荐理由",
            "rating": 4.5,
            "tags": ["标签1", "标签2"]
        }}
    ],
    "total": 5
}}"""

        prompt = f"用户需求：{user_input}\n\n请提供推荐（JSON格式，至少5个）。"
        
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
            
            recommendations = json.loads(response)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "message": "推荐已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成推荐失败: {str(e)}"}
