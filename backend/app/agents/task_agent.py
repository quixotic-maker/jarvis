"""任务管理Agent - 负责待办事项管理"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import TodoItem
from app.core.prompt_service import prompt_service


class TaskAgent(BaseAgent):
    """任务管理Agent，负责待办事项的创建、管理和跟踪"""
    
    def __init__(self):
        super().__init__(
            name="TaskAgent",
            description="负责待办事项管理，包括创建任务、设置优先级、跟踪进度"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务管理操作"""
        action = input_data.get("action", "create")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "create":
            return await self._create_task(user_input, db)
        elif action == "list":
            return await self._list_tasks(db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _create_task(self, user_input: str, db) -> Dict[str, Any]:
        """创建待办任务（集成Prompt系统）"""
        
        # 使用Prompt系统生成消息，带Few-shot示例
        current_date = datetime.now().strftime('%Y-%m-%d')
        messages = prompt_service.build_messages(
            agent_name="task_agent",
            user_input=user_input,
            use_few_shot=True,
            num_examples=2,
            context=f"当前日期：{current_date}"
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
            
            task_data = json.loads(response)
            
            todo = TodoItem(
                title=task_data.get("title", "未命名任务"),
                description=task_data.get("description", ""),
                priority=task_data.get("priority", "medium"),
                due_date=datetime.fromisoformat(task_data["due_date"]) if task_data.get("due_date") else None,
                tags=",".join(task_data.get("tags", []))
            )
            
            db.add(todo)
            db.commit()
            db.refresh(todo)
            
            return {
                "success": True,
                "message": "待办任务创建成功",
                "task": {
                    "id": todo.id,
                    "title": todo.title,
                    "priority": todo.priority,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None
                }
            }
        except Exception as e:
            return {"success": False, "error": f"创建任务失败: {str(e)}"}
    
    async def _list_tasks(self, db) -> Dict[str, Any]:
        """列出所有任务"""
        try:
            tasks = db.query(TodoItem).filter(
                TodoItem.is_completed == False
            ).order_by(TodoItem.priority.desc(), TodoItem.created_at).all()
            
            return {
                "success": True,
                "tasks": [{
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None
                } for t in tasks],
                "count": len(tasks)
            }
        except Exception as e:
            return {"success": False, "error": f"获取任务失败: {str(e)}"}
