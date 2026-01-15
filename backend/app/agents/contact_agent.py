"""联系人Agent - 负责联系人管理"""
from typing import Dict, Any
from datetime import datetime
import json

from app.agents.base_agent import BaseAgent
from app.db.models import Contact


class ContactAgent(BaseAgent):
    """联系人Agent，负责联系人管理和关系维护"""
    
    def __init__(self):
        super().__init__(
            name="ContactAgent",
            description="负责联系人管理、关系维护和沟通记录"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行联系人管理任务"""
        action = input_data.get("action", "add")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "add":
            return await self._add_contact(user_input, db)
        elif action == "search":
            return await self._search_contact(user_input, db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _add_contact(self, user_input: str, db) -> Dict[str, Any]:
        """添加联系人"""
        system_prompt = """你是一个联系人管理助手。从用户输入中提取联系人信息。

返回格式：
{
    "name": "姓名",
    "phone": "电话",
    "email": "邮箱",
    "company": "公司",
    "position": "职位",
    "tags": ["标签1", "标签2"],
    "notes": "备注"
}"""

        prompt = f"用户输入：{user_input}\n\n请提取联系人信息（JSON格式）。"
        
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
            
            contact_data = json.loads(response)
            
            contact = Contact(
                name=contact_data.get("name", "未知"),
                phone=contact_data.get("phone", ""),
                email=contact_data.get("email", ""),
                company=contact_data.get("company", ""),
                position=contact_data.get("position", ""),
                tags=",".join(contact_data.get("tags", [])),
                notes=contact_data.get("notes", "")
            )
            
            db.add(contact)
            db.commit()
            db.refresh(contact)
            
            return {
                "success": True,
                "message": "联系人添加成功",
                "contact": {
                    "id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone
                }
            }
        except Exception as e:
            return {"success": False, "error": f"添加联系人失败: {str(e)}"}
    
    async def _search_contact(self, query: str, db) -> Dict[str, Any]:
        """搜索联系人"""
        try:
            contacts = db.query(Contact).filter(
                Contact.name.contains(query) | Contact.company.contains(query)
            ).limit(10).all()
            
            return {
                "success": True,
                "contacts": [{
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "company": c.company
                } for c in contacts],
                "count": len(contacts)
            }
        except Exception as e:
            return {"success": False, "error": f"搜索联系人失败: {str(e)}"}
