"""总结Agent - 负责文本摘要和内容总结"""
from typing import Dict, Any

from app.agents.base_agent import BaseAgent


class SummaryAgent(BaseAgent):
    """总结Agent，负责文本摘要、内容总结和要点提取"""
    
    def __init__(self):
        super().__init__(
            name="SummaryAgent",
            description="负责文本摘要、长文总结和关键信息提取"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行总结任务
        
        Args:
            input_data: {
                "user_input": "用户输入",
                "parameters": {"length": "short/medium/long"}
            }
        """
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._summarize(user_input, parameters)
    
    async def _summarize(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """生成摘要"""
        length = parameters.get("length", "medium")
        length_guide = {
            "short": "1-2句话",
            "medium": "3-5句话",
            "long": "1段话"
        }
        
        system_prompt = f"""你是一个专业的文本总结助手。请对用户提供的内容进行总结。

要求：
- 摘要长度：{length_guide.get(length, '适中')}
- 保留关键信息和要点
- 语言简洁清晰
- 提取核心观点

同时提供：
1. 简短摘要
2. 关键要点列表
3. 主要结论"""

        prompt = f"请总结以下内容：\n\n{user_input}"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "summary": response,
                "message": "总结完成",
                "length": length
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"总结失败: {str(e)}"
            }
