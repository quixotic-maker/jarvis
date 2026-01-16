"""信息检索Agent - 负责信息搜索和检索"""
from typing import Dict, Any
import aiohttp

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service


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
        
        # 使用Prompt系统
        messages = prompt_service.build_messages(
            agent_name="info_retrieval",
            user_input=query,
            use_few_shot=False,  # InfoRetrieval通用性强，暂不用Few-shot
            constraints=["提供准确信息", "不确定时说明", "不编造信息"]
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else query
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
            
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
