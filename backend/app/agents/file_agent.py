"""文件Agent - 负责文件管理和操作"""
from typing import Dict, Any
import json
import os

from app.agents.base_agent import BaseAgent


class FileAgent(BaseAgent):
    """文件Agent，负责文件的创建、搜索和管理"""
    
    def __init__(self):
        super().__init__(
            name="FileAgent",
            description="负责文件管理、搜索和组织"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件相关任务
        
        Args:
            input_data: {
                "action": "search/organize/info",
                "user_input": "用户输入"
            }
        """
        action = input_data.get("action", "search")
        user_input = input_data.get("user_input", "")
        
        if action == "search":
            return await self._search_files(user_input)
        elif action == "organize":
            return await self._organize_files(user_input)
        elif action == "info":
            return await self._file_info(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _search_files(self, user_input: str) -> Dict[str, Any]:
        """搜索文件（使用LLM解析需求）"""
        system_prompt = """你是一个文件管理助手。根据用户需求，提供文件搜索建议。

返回格式：
{
    "search_keywords": ["关键词1", "关键词2"],
    "file_types": [".pdf", ".docx"],
    "suggestions": "搜索建议"
}"""

        prompt = f"用户需求：{user_input}\n\n请分析文件搜索需求（JSON格式）。"
        
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
            
            search_data = json.loads(response)
            
            return {
                "success": True,
                "search_params": search_data,
                "message": "文件搜索建议已生成",
                "note": "演示模式 - 实际应用中需要文件系统访问权限"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件搜索失败: {str(e)}"
            }
    
    async def _organize_files(self, user_input: str) -> Dict[str, Any]:
        """文件整理建议"""
        system_prompt = """你是一个文件整理专家。提供文件组织和整理建议。"""
        
        prompt = f"用户需求：{user_input}\n\n请提供文件整理建议。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "suggestions": response,
                "message": "文件整理建议已生成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成建议失败: {str(e)}"
            }
    
    async def _file_info(self, user_input: str) -> Dict[str, Any]:
        """文件信息查询"""
        return {
            "success": True,
            "message": "文件信息查询功能",
            "note": "演示模式"
        }
