"""邮件Agent - 负责邮件管理和发送"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent


class EmailAgent(BaseAgent):
    """邮件Agent，负责邮件的创建、发送和管理"""
    
    def __init__(self):
        super().__init__(
            name="EmailAgent",
            description="负责邮件管理，包括撰写、发送和读取邮件"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行邮件相关任务
        
        Args:
            input_data: {
                "action": "compose/send/read",
                "user_input": "用户原始输入",
                "db": "数据库会话"
            }
        """
        action = input_data.get("action", "compose")
        user_input = input_data.get("user_input", "")
        
        if action == "compose":
            return await self._compose_email(user_input)
        elif action == "send":
            return await self._send_email(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _compose_email(self, user_input: str) -> Dict[str, Any]:
        """使用LLM撰写邮件"""
        system_prompt = """你是一个专业的邮件撰写助手。根据用户的需求，生成合适的邮件内容。

返回格式：
{
    "subject": "邮件主题",
    "to": "收件人",
    "body": "邮件正文",
    "tone": "formal/casual"
}"""

        prompt = f"用户需求：{user_input}\n\n请生成邮件内容。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            # 清理并解析JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            email_data = json.loads(response)
            
            return {
                "success": True,
                "message": "邮件已生成",
                "email": email_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成邮件失败: {str(e)}"
            }
    
    async def _send_email(self, user_input: str) -> Dict[str, Any]:
        """发送邮件（模拟）"""
        return {
            "success": True,
            "message": "邮件发送功能（演示模式）",
            "note": "实际应用中需要集成SMTP服务"
        }
