"""信息检索Agent - 负责信息搜索和检索"""
from typing import Dict, Any
import aiohttp

from app.agents.base_agent import BaseAgent


class InfoRetrievalAgent(BaseAgent):
    """信息检索Agent，负责搜索和检索信息"""
    
    def __init__(self):
        super().__init__(
            name="InfoRetrievalAgent",
            description="负责信息检索和搜索"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行信息检索任务
        
        Args:
            input_data: {
                "query": "搜索查询",
                "user_input": "用户原始输入"
            }
        """
        user_input = input_data.get("user_input", "")
        query = input_data.get("query", user_input)
        
        # 使用LLM提供答案（实际应用中可以集成真实的搜索API）
        system_prompt = """你是一个信息检索助手。根据用户的问题，提供准确、有用的信息。
如果你不确定答案，请诚实地说明，不要编造信息。"""

        prompt = f"用户问题：{query}\n\n请提供详细的答案。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "query": query,
                "answer": response,
                "source": "LLM Generated"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"信息检索失败: {str(e)}"
            }
