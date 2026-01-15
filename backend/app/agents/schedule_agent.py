"""日程Agent - 负责日程管理"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import Schedule


class ScheduleAgent(BaseAgent):
    """日程Agent，负责创建、查询和管理日程"""
    
    def __init__(self):
        super().__init__(
            name="ScheduleAgent",
            description="负责日程管理，包括创建、查询、修改日程"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行日程相关任务
        
        Args:
            input_data: {
                "action": "create/query/update/delete",
                "user_input": "用户原始输入",
                "db": "数据库会话"
            }
        """
        action = input_data.get("action", "create")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "create":
            return await self._create_schedule(user_input, db)
        elif action == "query":
            return await self._query_schedules(user_input, db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _create_schedule(self, user_input: str, db) -> Dict[str, Any]:
        """从自然语言创建日程"""
        system_prompt = """你是一个日程管理助手。根据用户的自然语言输入，提取日程信息并返回结构化的JSON数据。

返回格式：
{
    "title": "日程标题",
    "description": "详细描述",
    "start_time": "YYYY-MM-DD HH:MM:SS",
    "end_time": "YYYY-MM-DD HH:MM:SS",
    "location": "地点（如果有）"
}

如果没有明确指定时间，使用合理的默认值。"""

        prompt = f"用户输入：{user_input}\n\n请提取日程信息并返回JSON格式。"
        
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
            
            schedule_data = json.loads(response)
            
            # 创建日程记录
            schedule = Schedule(
                title=schedule_data.get("title", "未命名日程"),
                description=schedule_data.get("description", ""),
                start_time=datetime.fromisoformat(schedule_data["start_time"]),
                end_time=datetime.fromisoformat(schedule_data["end_time"]) if schedule_data.get("end_time") else None,
                location=schedule_data.get("location", "")
            )
            
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            
            return {
                "success": True,
                "message": "日程创建成功",
                "schedule": {
                    "id": schedule.id,
                    "title": schedule.title,
                    "description": schedule.description,
                    "start_time": schedule.start_time.isoformat(),
                    "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
                    "location": schedule.location
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"创建日程失败: {str(e)}"
            }
    
    async def _query_schedules(self, user_input: str, db) -> Dict[str, Any]:
        """查询日程"""
        try:
            # 查询最近的日程
            schedules = db.query(Schedule).order_by(Schedule.start_time.desc()).limit(10).all()
            
            schedule_list = [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "location": s.location,
                    "is_completed": s.is_completed
                }
                for s in schedules
            ]
            
            return {
                "success": True,
                "schedules": schedule_list,
                "count": len(schedule_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"查询日程失败: {str(e)}"
            }
