"""
Prompt模板系统
提供统一的Prompt管理和组装能力
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json


class PromptType(str, Enum):
    """Prompt类型"""
    SYSTEM = "system"  # 系统Prompt，定义Agent角色
    INSTRUCTION = "instruction"  # 指令Prompt，任务说明
    FEW_SHOT = "few_shot"  # Few-shot示例
    COT = "chain_of_thought"  # 思维链提示
    CONSTRAINT = "constraint"  # 约束条件
    OUTPUT_FORMAT = "output_format"  # 输出格式要求


class PromptTemplate:
    """Prompt模板基类"""
    
    def __init__(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        version: str = "1.0"
    ):
        """
        初始化Prompt模板
        
        Args:
            name: 模板名称
            template: 模板内容（支持{variable}占位符）
            description: 模板描述
            variables: 需要的变量列表
            examples: Few-shot示例
            version: 版本号
        """
        self.name = name
        self.template = template
        self.description = description
        self.variables = variables or []
        self.examples = examples or []
        self.version = version
        self.created_at = datetime.now()
    
    def render(self, **kwargs) -> str:
        """
        渲染模板
        
        Args:
            **kwargs: 变量值
        
        Returns:
            渲染后的Prompt
        """
        # 检查必需变量
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"缺少必需变量: {missing_vars}")
        
        # 渲染模板
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"模板变量错误: {e}")
    
    def add_example(self, input_text: str, output_text: str):
        """添加Few-shot示例"""
        self.examples.append({
            "input": input_text,
            "output": output_text
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "examples": self.examples,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """从字典创建"""
        return cls(
            name=data["name"],
            template=data["template"],
            description=data.get("description", ""),
            variables=data.get("variables", []),
            examples=data.get("examples", []),
            version=data.get("version", "1.0")
        )


class AgentPromptBuilder:
    """Agent Prompt构建器"""
    
    def __init__(self, agent_name: str):
        """
        初始化构建器
        
        Args:
            agent_name: Agent名称
        """
        self.agent_name = agent_name
        self.prompts: Dict[PromptType, str] = {}
        self.context: Dict[str, Any] = {}
    
    def set_system_prompt(self, prompt: str) -> "AgentPromptBuilder":
        """设置系统Prompt"""
        self.prompts[PromptType.SYSTEM] = prompt
        return self
    
    def set_instruction(self, instruction: str) -> "AgentPromptBuilder":
        """设置指令Prompt"""
        self.prompts[PromptType.INSTRUCTION] = instruction
        return self
    
    def add_few_shot_examples(self, examples: List[Dict[str, str]]) -> "AgentPromptBuilder":
        """添加Few-shot示例"""
        examples_text = "\n\n示例:\n"
        for i, example in enumerate(examples, 1):
            examples_text += f"\n示例{i}:\n"
            examples_text += f"输入: {example['input']}\n"
            examples_text += f"输出: {example['output']}\n"
        
        self.prompts[PromptType.FEW_SHOT] = examples_text
        return self
    
    def add_cot_prompt(self, cot_instruction: str) -> "AgentPromptBuilder":
        """添加思维链提示"""
        self.prompts[PromptType.COT] = cot_instruction
        return self
    
    def add_constraints(self, constraints: List[str]) -> "AgentPromptBuilder":
        """添加约束条件"""
        constraints_text = "\n约束条件:\n"
        for constraint in constraints:
            constraints_text += f"- {constraint}\n"
        
        self.prompts[PromptType.CONSTRAINT] = constraints_text
        return self
    
    def set_output_format(self, format_description: str) -> "AgentPromptBuilder":
        """设置输出格式"""
        self.prompts[PromptType.OUTPUT_FORMAT] = f"\n输出格式:\n{format_description}"
        return self
    
    def add_context(self, key: str, value: Any) -> "AgentPromptBuilder":
        """添加上下文信息"""
        self.context[key] = value
        return self
    
    def build(self) -> str:
        """构建最终Prompt"""
        parts = []
        
        # 1. 系统Prompt（Agent角色定位）
        if PromptType.SYSTEM in self.prompts:
            parts.append(self.prompts[PromptType.SYSTEM])
        
        # 2. 指令Prompt
        if PromptType.INSTRUCTION in self.prompts:
            parts.append(self.prompts[PromptType.INSTRUCTION])
        
        # 3. 约束条件
        if PromptType.CONSTRAINT in self.prompts:
            parts.append(self.prompts[PromptType.CONSTRAINT])
        
        # 4. Few-shot示例
        if PromptType.FEW_SHOT in self.prompts:
            parts.append(self.prompts[PromptType.FEW_SHOT])
        
        # 5. 思维链提示
        if PromptType.COT in self.prompts:
            parts.append(self.prompts[PromptType.COT])
        
        # 6. 输出格式
        if PromptType.OUTPUT_FORMAT in self.prompts:
            parts.append(self.prompts[PromptType.OUTPUT_FORMAT])
        
        # 7. 上下文信息
        if self.context:
            context_text = "\n当前上下文:\n"
            for key, value in self.context.items():
                context_text += f"- {key}: {value}\n"
            parts.append(context_text)
        
        return "\n\n".join(parts)
    
    def build_messages(self) -> List[Dict[str, str]]:
        """构建消息列表（适用于Chat API）"""
        messages = []
        
        # System消息
        if PromptType.SYSTEM in self.prompts:
            messages.append({
                "role": "system",
                "content": self.prompts[PromptType.SYSTEM]
            })
        
        # 组装其他部分作为user消息
        other_parts = []
        for prompt_type in [PromptType.INSTRUCTION, PromptType.CONSTRAINT, 
                           PromptType.FEW_SHOT, PromptType.COT, PromptType.OUTPUT_FORMAT]:
            if prompt_type in self.prompts:
                other_parts.append(self.prompts[prompt_type])
        
        if self.context:
            context_text = "\n当前上下文:\n"
            for key, value in self.context.items():
                context_text += f"- {key}: {value}\n"
            other_parts.append(context_text)
        
        if other_parts:
            messages.append({
                "role": "user",
                "content": "\n\n".join(other_parts)
            })
        
        return messages


class PromptLibrary:
    """Prompt模板库"""
    
    def __init__(self):
        """初始化模板库"""
        self.templates: Dict[str, PromptTemplate] = {}
    
    def register(self, template: PromptTemplate):
        """注册模板"""
        self.templates[template.name] = template
    
    def get(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板名称"""
        return list(self.templates.keys())
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {
            name: template.to_dict()
            for name, template in self.templates.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for name, template_data in data.items():
            template = PromptTemplate.from_dict(template_data)
            self.register(template)


# 全局Prompt库实例
prompt_library = PromptLibrary()
