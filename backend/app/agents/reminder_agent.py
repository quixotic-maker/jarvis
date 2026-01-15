"""提醒Agent - 负责设置和管理提醒"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import Reminder


class ReminderAgent(BaseAgent):
    """提醒Agent，负责创建、管理和触发提醒"""
    
    def __init__(self):
        super().__init__(
            name="ReminderAgent",
            description="负责创建定时提醒、重复提醒和智能提醒"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行提醒相关任务
        
        Args:
            input_data: {
                "action": "create/list/delete",
                "user_input": "用户输入",
                "db": "数据库会话"
            }
        """
        action = input_data.get("action", "create")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "create":
            return await self._create_reminder(user_input, db)
        elif action == "list":
            return await self._list_reminders(db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _create_reminder(self, user_input: str, db) -> Dict[str, Any]:
        """创建提醒"""
        system_prompt = """你是一个提醒助手。根据用户输入创建提醒。

返回格式：
{
    "title": "提醒标题",
    "message": "提醒内容",
    "remind_at": "YYYY-MM-DD HH:MM:SS",
    "repeat": "once/daily/weekly/monthly",
    "priority": "low/medium/high"
}"""

        prompt = f"用户输入：{user_input}\n\n请创建提醒（JSON格式）。"
        
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
            
            reminder_data = json.loads(response)
            
            # 创建提醒记录
            reminder = Reminder(
                title=reminder_data.get("title", "未命名提醒"),
                message=reminder_data.get("message", ""),
                remind_at=datetime.fromisoformat(reminder_data["remind_at"]),
                repeat_type=reminder_data.get("repeat", "once"),
                priority=reminder_data.get("priority", "medium")
            )
            
            db.add(reminder)
            db.commit()
            db.refresh(reminder)
            
            return {
                "success": True,
                "message": "提醒创建成功",
                "reminder": {
                    "id": reminder.id,
                    "title": reminder.title,
                    "message": reminder.message,
                    "remind_at": reminder.remind_at.isoformat(),
                    "repeat_type": reminder.repeat_type
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"创建提醒失败: {str(e)}"
            }
    
    async def _list_reminders(self, db) -> Dict[str, Any]:
        """列出所有提醒"""
        try:
            reminders = db.query(Reminder).filter(
                Reminder.is_triggered == False
            ).order_by(Reminder.remind_at).all()
            
            reminder_list = [
                {
                    "id": r.id,
                    "title": r.title,
                    "message": r.message,
                    "remind_at": r.remind_at.isoformat(),
                    "repeat_type": r.repeat_type,
                    "priority": r.priority
                }
                for r in reminders
            ]
            
            return {
                "success": True,
                "reminders": reminder_list,
                "count": len(reminder_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取提醒失败: {str(e)}"
            }
