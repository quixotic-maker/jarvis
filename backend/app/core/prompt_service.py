"""
Prompt助手服务
提供统一的Prompt生成和管理接口
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.prompt_template import AgentPromptBuilder, PromptTemplate, prompt_library
from app.core.cot_prompts import ChainOfThoughtBuilder, CoTPattern
from app.core.few_shot_examples import FewShotExamples, create_few_shot_prompt
from app.core.agent_prompts import initialize_agent_prompts


class PromptService:
    """Prompt服务类"""
    
    def __init__(self):
        """初始化服务"""
        # 确保Agent Prompts已初始化
        self.library = prompt_library
    
    def get_agent_system_prompt(
        self,
        agent_name: str,
        **variables
    ) -> str:
        """
        获取Agent的系统Prompt
        
        Args:
            agent_name: Agent名称
            **variables: 模板变量
        
        Returns:
            系统Prompt文本
        """
        template_name = f"{agent_name.lower()}_system"
        template = self.library.get(template_name)
        
        if not template:
            # 如果没有找到模板，返回通用Prompt
            return f"你是{agent_name}，一个专业的AI助手。"
        
        # 如果有变量，渲染模板；否则返回原始模板
        if variables and template.variables:
            try:
                return template.render(**variables)
            except ValueError:
                # 缺少变量时返回原始模板
                return template.template
        
        return template.template
    
    def build_agent_prompt(
        self,
        agent_name: str,
        user_input: str,
        use_cot: bool = False,
        cot_pattern: Optional[CoTPattern] = None,
        use_few_shot: bool = False,
        num_examples: int = 2,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
        output_format: Optional[str] = None
    ) -> str:
        """
        构建完整的Agent Prompt
        
        Args:
            agent_name: Agent名称
            user_input: 用户输入
            use_cot: 是否使用Chain-of-Thought
            cot_pattern: CoT模式
            use_few_shot: 是否使用Few-shot示例
            num_examples: Few-shot示例数量
            context: 上下文信息
            constraints: 约束条件
            output_format: 输出格式要求
        
        Returns:
            完整的Prompt
        """
        builder = AgentPromptBuilder(agent_name)
        
        # 1. 设置系统Prompt
        system_prompt = self.get_agent_system_prompt(
            agent_name,
            current_date=datetime.now().strftime("%Y年%m月%d日")
        )
        builder.set_system_prompt(system_prompt)
        
        # 2. 设置用户指令
        builder.set_instruction(f"用户需求: {user_input}")
        
        # 3. 添加约束条件
        if constraints:
            builder.add_constraints(constraints)
        
        # 4. 添加Few-shot示例
        if use_few_shot:
            examples = FewShotExamples.get_examples(agent_name, num_examples)
            if examples:
                builder.add_few_shot_examples(examples)
        
        # 5. 添加Chain-of-Thought提示
        if use_cot and cot_pattern:
            cot_prompt = ChainOfThoughtBuilder.get_cot_prompt(
                cot_pattern,
                task_description=user_input
            )
            builder.add_cot_prompt(cot_prompt)
        
        # 6. 设置输出格式
        if output_format:
            builder.set_output_format(output_format)
        
        # 7. 添加上下文
        if context:
            for key, value in context.items():
                builder.add_context(key, value)
        
        return builder.build()
    
    def build_messages(
        self,
        agent_name: str,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        构建消息列表（适用于Chat API）
        
        Args:
            agent_name: Agent名称
            user_input: 用户输入
            conversation_history: 对话历史
            **kwargs: 其他参数（同build_agent_prompt）
        
        Returns:
            消息列表
        """
        messages = []
        
        # 1. 系统消息
        system_prompt = self.get_agent_system_prompt(
            agent_name,
            current_date=datetime.now().strftime("%Y年%m月%d日")
        )
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 2. 添加Few-shot示例（作为历史对话）
        if kwargs.get('use_few_shot', False):
            examples = FewShotExamples.get_examples(
                agent_name,
                kwargs.get('num_examples', 2)
            )
            for example in examples:
                messages.append({
                    "role": "user",
                    "content": example.get('input', '')
                })
                output = example.get('output', {})
                if isinstance(output, dict):
                    import json
                    output_text = json.dumps(output, ensure_ascii=False, indent=2)
                else:
                    output_text = str(output)
                messages.append({
                    "role": "assistant",
                    "content": output_text
                })
        
        # 3. 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 4. 添加当前用户输入
        user_message = user_input
        
        # 添加CoT提示
        if kwargs.get('use_cot', False) and kwargs.get('cot_pattern'):
            cot_prompt = ChainOfThoughtBuilder.get_cot_prompt(
                kwargs['cot_pattern'],
                task_description=user_input
            )
            user_message = f"{cot_prompt}\n\n{user_input}"
        
        # 添加约束条件
        if kwargs.get('constraints'):
            constraints_text = "\n约束条件:\n" + "\n".join(
                f"- {c}" for c in kwargs['constraints']
            )
            user_message += f"\n\n{constraints_text}"
        
        # 添加输出格式
        if kwargs.get('output_format'):
            user_message += f"\n\n输出格式:\n{kwargs['output_format']}"
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def optimize_prompt(
        self,
        prompt: str,
        optimization_goals: List[str] = None
    ) -> str:
        """
        优化Prompt
        
        Args:
            prompt: 原始Prompt
            optimization_goals: 优化目标（如"更具体"、"更简洁"）
        
        Returns:
            优化后的Prompt
        """
        # TODO: 实现Prompt优化逻辑
        # 可以使用LLM来优化Prompt本身
        return prompt
    
    def evaluate_prompt(
        self,
        prompt: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        评估Prompt效果
        
        Args:
            prompt: Prompt文本
            test_cases: 测试用例
        
        Returns:
            评估结果
        """
        # TODO: 实现Prompt评估逻辑
        return {
            "accuracy": 0.0,
            "clarity": 0.0,
            "consistency": 0.0
        }


# 全局Prompt服务实例
prompt_service = PromptService()


# 便捷函数
def get_agent_prompt(
    agent_name: str,
    user_input: str,
    **kwargs
) -> str:
    """
    快速获取Agent Prompt
    
    Args:
        agent_name: Agent名称
        user_input: 用户输入
        **kwargs: 其他参数
    
    Returns:
        Prompt文本
    """
    return prompt_service.build_agent_prompt(agent_name, user_input, **kwargs)


def get_agent_messages(
    agent_name: str,
    user_input: str,
    **kwargs
) -> List[Dict[str, str]]:
    """
    快速获取Agent消息列表
    
    Args:
        agent_name: Agent名称
        user_input: 用户输入
        **kwargs: 其他参数
    
    Returns:
        消息列表
    """
    return prompt_service.build_messages(agent_name, user_input, **kwargs)
