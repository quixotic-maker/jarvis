"""学习Agent - 负责学习辅助和知识管理"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service


class LearningAgent(BaseAgent):
    """学习Agent，负责学习计划、知识整理和学习建议"""
    
    def __init__(self):
        super().__init__(
            name="LearningAgent",
            description="负责制定学习计划、知识点整理、学习建议和进度跟踪"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行学习辅助任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        action = parameters.get("action", "plan")
        
        if action == "plan":
            return await self._create_learning_plan(user_input)
        elif action == "explain":
            return await self._explain_concept(user_input)
        elif action == "quiz":
            return await self._generate_quiz(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _create_learning_plan(self, topic: str) -> Dict[str, Any]:
        """创建学习计划（集成Prompt系统）"""
        
        # 使用Prompt系统
        messages = prompt_service.build_messages(
            agent_name="learning_agent",
            user_input=f"制定学习计划：{topic}",
            use_few_shot=False,
            output_format="{\"topic\": \"...\", \"duration\": \"...\", \"phases\": [...], \"tips\": [...]}"
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else topic
        
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
            
            plan = json.loads(response)
            
            return {
                "success": True,
                "learning_plan": plan,
                "message": "学习计划已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"生成学习计划失败: {str(e)}"}
    
    async def _explain_concept(self, concept: str) -> Dict[str, Any]:
        """解释概念"""
        system_prompt = """你是一个知识导师。用简单易懂的方式解释复杂概念。

包括：
1. 核心定义
2. 通俗解释
3. 实际案例
4. 相关知识"""

        prompt = f"请解释这个概念：{concept}"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "explanation": response,
                "message": "概念解释完成"
            }
        except Exception as e:
            return {"success": False, "error": f"解释概念失败: {str(e)}"}
    
    async def _generate_quiz(self, topic: str) -> Dict[str, Any]:
        """生成测验"""
        system_prompt = """你是一个测验出题专家。根据主题生成测验题目。

返回格式：
{
    "questions": [
        {
            "question": "题目",
            "options": ["A", "B", "C", "D"],
            "answer": "正确答案",
            "explanation": "答案解释"
        }
    ]
}"""

        prompt = f"主题：{topic}\n\n请生成5道测验题（JSON格式）。"
        
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
            
            quiz = json.loads(response)
            
            return {
                "success": True,
                "quiz": quiz,
                "message": "测验生成成功"
            }
        except Exception as e:
            return {"success": False, "error": f"生成测验失败: {str(e)}"}
