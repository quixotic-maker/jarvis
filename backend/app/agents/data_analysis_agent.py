"""数据分析Agent - 负责数据分析和可视化"""
from typing import Dict, Any
import json

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service
from app.core.cot_prompts import CoTPattern


class DataAnalysisAgent(BaseAgent):
    """数据分析Agent，负责数据分析、统计和洞察"""
    
    def __init__(self):
        super().__init__(
            name="DataAnalysisAgent",
            description="负责数据分析、统计计算、趋势分析和数据洞察"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据分析任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._analyze_data(user_input, parameters)
    
    async def _analyze_data(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """分析数据（集成Prompt系统，使用CoT）"""
        
        # 使用Prompt系统，带Few-shot和CoT
        messages = prompt_service.build_messages(
            agent_name="data_analysis",
            user_input=user_input,
            use_few_shot=True,
            num_examples=1,
            use_cot=True,
            cot_pattern=CoTPattern.ANALYSIS,  # 使用分析模式
            output_format="{\"analysis_type\": \"...\", \"findings\": [...], \"statistics\": {...}, \"recommendations\": [...], \"visualization_suggestion\": \"...\"}"
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
            
            analysis = json.loads(response)
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "数据分析完成"
            }
        except Exception as e:
            return {"success": False, "error": f"数据分析失败: {str(e)}"}
