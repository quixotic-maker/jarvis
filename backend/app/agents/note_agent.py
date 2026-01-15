"""笔记Agent - 负责笔记管理"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import Note


class NoteAgent(BaseAgent):
    """笔记Agent，负责笔记的创建、搜索和管理"""
    
    def __init__(self):
        super().__init__(
            name="NoteAgent",
            description="负责笔记管理，包括创建、搜索、分类和标签管理"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行笔记操作"""
        action = input_data.get("action", "create")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "create":
            return await self._create_note(user_input, db)
        elif action == "search":
            return await self._search_notes(user_input, db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _create_note(self, user_input: str, db) -> Dict[str, Any]:
        """创建笔记"""
        system_prompt = """你是一个笔记助手。根据用户输入创建笔记。

返回格式：
{
    "title": "笔记标题",
    "content": "笔记内容",
    "category": "分类",
    "tags": ["标签1", "标签2"]
}"""

        prompt = f"用户输入：{user_input}\n\n请创建笔记（JSON格式）。"
        
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
            
            note_data = json.loads(response)
            
            note = Note(
                title=note_data.get("title", "无标题笔记"),
                content=note_data.get("content", ""),
                category=note_data.get("category", "未分类"),
                tags=",".join(note_data.get("tags", []))
            )
            
            db.add(note)
            db.commit()
            db.refresh(note)
            
            return {
                "success": True,
                "message": "笔记创建成功",
                "note": {
                    "id": note.id,
                    "title": note.title,
                    "category": note.category
                }
            }
        except Exception as e:
            return {"success": False, "error": f"创建笔记失败: {str(e)}"}
    
    async def _search_notes(self, user_input: str, db) -> Dict[str, Any]:
        """搜索笔记"""
        try:
            notes = db.query(Note).filter(
                Note.title.contains(user_input) | Note.content.contains(user_input)
            ).limit(10).all()
            
            return {
                "success": True,
                "notes": [{
                    "id": n.id,
                    "title": n.title,
                    "category": n.category,
                    "created_at": n.created_at.isoformat()
                } for n in notes],
                "count": len(notes)
            }
        except Exception as e:
            return {"success": False, "error": f"搜索笔记失败: {str(e)}"}
