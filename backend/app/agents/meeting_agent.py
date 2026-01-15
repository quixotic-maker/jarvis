"""会议Agent - 负责会议管理"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import Meeting


class MeetingAgent(BaseAgent):
    """会议Agent，负责会议安排、纪要和跟进"""
    
    def __init__(self):
        super().__init__(
            name="MeetingAgent",
            description="负责会议安排、参会人管理、会议纪要和行动项跟进"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行会议管理任务"""
        action = input_data.get("action", "schedule")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "schedule":
            return await self._schedule_meeting(user_input, db)
        elif action == "minutes":
            return await self._generate_minutes(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _schedule_meeting(self, user_input: str, db) -> Dict[str, Any]:
        """安排会议"""
        system_prompt = """你是一个会议助手。根据用户输入安排会议。

返回格式：
{
    "title": "会议主题",
    "start_time": "YYYY-MM-DD HH:MM:SS",
    "duration": 60,
    "attendees": ["参会人1", "参会人2"],
    "location": "会议地点",
    "agenda": "会议议程"
}"""

        prompt = f"用户输入：{user_input}\n\n请安排会议（JSON格式）。"
        
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
            
            meeting_data = json.loads(response)
            
            meeting = Meeting(
                title=meeting_data.get("title", "未命名会议"),
                start_time=datetime.fromisoformat(meeting_data["start_time"]),
                duration=meeting_data.get("duration", 60),
                attendees=",".join(meeting_data.get("attendees", [])),
                location=meeting_data.get("location", ""),
                agenda=meeting_data.get("agenda", "")
            )
            
            db.add(meeting)
            db.commit()
            db.refresh(meeting)
            
            return {
                "success": True,
                "message": "会议安排成功",
                "meeting": {
                    "id": meeting.id,
                    "title": meeting.title,
                    "start_time": meeting.start_time.isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": f"安排会议失败: {str(e)}"}
    
    async def _generate_minutes(self, discussion: str) -> Dict[str, Any]:
        """生成会议纪要"""
        system_prompt = """你是一个会议记录专家。根据讨论内容生成专业的会议纪要。

包括：
1. 会议要点
2. 讨论内容
3. 决策事项
4. 行动计划"""

        prompt = f"会议讨论内容：\n{discussion}\n\n请生成会议纪要。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "minutes": response,
                "message": "会议纪要生成成功"
            }
        except Exception as e:
            return {"success": False, "error": f"生成会议纪要失败: {str(e)}"}
