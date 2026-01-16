"""代码Agent - 负责代码生成和解释"""
from typing import Dict, Any

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service
from app.core.cot_prompts import CoTPattern


class CodeAgent(BaseAgent):
    """代码Agent，负责代码生成、解释和优化"""
    
    def __init__(self):
        super().__init__(
            name="CodeAgent",
            description="负责代码生成、代码解释、bug修复和代码优化"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行代码相关任务"""
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        action = parameters.get("action", "generate")
        
        if action == "generate":
            return await self._generate_code(user_input, parameters)
        elif action == "explain":
            return await self._explain_code(user_input)
        elif action == "optimize":
            return await self._optimize_code(user_input)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _generate_code(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """生成代码（集成Prompt系统）"""
        language = parameters.get("language", "Python")
        
        # 使用Prompt系统，带Few-shot和CoT（代码生成需要逐步思考）
        messages = prompt_service.build_messages(
            agent_name="code_agent",
            user_input=user_input,
            use_few_shot=True,
            num_examples=1,
            use_cot=True,
            cot_pattern=CoTPattern.PROBLEM_SOLVING,  # 使用问题解决模式
            constraints=[
                "代码要简洁、高效、可读",
                "添加必要的注释",
                "遵循最佳实践",
                "处理边界情况"
            ],
            output_format=f"```{language.lower()}\\n[代码]\\n```\\n\\n解释：[说明]"
        )
        
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else user_input
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
            
            return {
                "success": True,
                "language": language,
                "code": response,
                "message": "代码生成成功"
            }
        except Exception as e:
            return {"success": False, "error": f"代码生成失败: {str(e)}"}
    
    async def _explain_code(self, code: str) -> Dict[str, Any]:
        """解释代码"""
        system_prompt = """你是一个代码解释专家。请详细解释代码的功能、逻辑和关键点。"""
        
        prompt = f"请解释这段代码：\n\n{code}"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "explanation": response,
                "message": "代码解释完成"
            }
        except Exception as e:
            return {"success": False, "error": f"代码解释失败: {str(e)}"}
    
    async def _optimize_code(self, code: str) -> Dict[str, Any]:
        """优化代码"""
        system_prompt = """你是一个代码优化专家。请优化代码的性能、可读性和结构。"""
        
        prompt = f"请优化这段代码：\n\n{code}"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "optimized_code": response,
                "message": "代码优化完成"
            }
        except Exception as e:
            return {"success": False, "error": f"代码优化失败: {str(e)}"}
