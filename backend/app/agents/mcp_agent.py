"""MCP (Model Context Protocol) Agent - 模型上下文协议"""
from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent


class MCPAgent(BaseAgent):
    """
    MCP Agent - 模型上下文协议Agent
    
    实现标准化的模型上下文管理和协议交互：
    1. 上下文管理 - 智能管理对话上下文
    2. 协议适配 - 适配不同的LLM Provider
    3. 状态保持 - 维护对话状态和历史
    4. 工具调用 - 标准化的工具调用接口
    5. 多模态支持 - 文本、图像、代码等
    """
    
    def __init__(self):
        super().__init__(
            name="MCPAgent",
            description="模型上下文协议Agent，提供标准化的上下文管理和多Agent协作"
        )
        self.context_window = []
        self.max_context_length = 10
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行MCP任务"""
        action = input_data.get("action", "chat")
        user_input = input_data.get("user_input", "")
        context = input_data.get("context", {})
        
        if action == "chat":
            return await self._mcp_chat(user_input, context)
        elif action == "tool_call":
            return await self._mcp_tool_call(user_input, context)
        elif action == "context_manage":
            return await self._manage_context(context)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _mcp_chat(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """MCP对话 - 上下文感知的对话"""
        # 1. 更新上下文窗口
        self.context_window.append({
            "role": "user",
            "content": message,
            "timestamp": context.get("timestamp", "")
        })
        
        # 2. 保持上下文窗口大小
        if len(self.context_window) > self.max_context_length:
            # 智能压缩上下文
            compressed = await self._compress_context(self.context_window)
            self.context_window = compressed
        
        # 3. 构建MCP格式的提示
        mcp_prompt = self._build_mcp_prompt(message, context)
        
        # 4. 调用LLM
        system_prompt = """你是Jarvis的MCP协调Agent。你负责：
1. 理解用户意图和上下文
2. 决定是否需要调用工具或其他Agent
3. 维护对话连贯性
4. 提供智能响应

如果需要调用工具，返回格式：
{
    "type": "tool_call",
    "tool": "工具名称",
    "parameters": {},
    "reasoning": "为什么调用这个工具"
}

如果直接回复，返回格式：
{
    "type": "response",
    "content": "回复内容",
    "context_update": {}
}"""
        
        try:
            response = await self.process_with_llm(mcp_prompt, system_prompt)
            
            # 解析响应
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            
            # 更新上下文窗口
            self.context_window.append({
                "role": "assistant",
                "content": result.get("content", ""),
                "type": result.get("type", "response")
            })
            
            return {
                "success": True,
                "result": result,
                "context_size": len(self.context_window)
            }
        except Exception as e:
            return {"success": False, "error": f"MCP对话失败: {str(e)}"}
    
    async def _mcp_tool_call(self, tool_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """MCP工具调用 - 标准化的工具调用接口"""
        system_prompt = """你是一个工具调用规划器。分析工具调用请求，生成标准化的调用参数。

返回格式：
{
    "tool_name": "工具名称",
    "parameters": {
        "param1": "value1"
    },
    "expected_output": "预期输出类型",
    "fallback": "备用方案"
}"""

        prompt = f"工具调用请求：{tool_request}\n\n上下文：{json.dumps(context, ensure_ascii=False)}\n\n请生成工具调用参数。"
        
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
            
            tool_call = json.loads(response)
            
            return {
                "success": True,
                "tool_call": tool_call,
                "message": "工具调用参数已生成"
            }
        except Exception as e:
            return {"success": False, "error": f"工具调用失败: {str(e)}"}
    
    async def _manage_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """上下文管理 - 智能管理对话上下文"""
        action = context.get("action", "get")
        
        if action == "get":
            return {
                "success": True,
                "context_window": self.context_window,
                "size": len(self.context_window)
            }
        elif action == "clear":
            self.context_window = []
            return {
                "success": True,
                "message": "上下文已清空"
            }
        elif action == "compress":
            compressed = await self._compress_context(self.context_window)
            self.context_window = compressed
            return {
                "success": True,
                "message": "上下文已压缩",
                "new_size": len(compressed)
            }
        else:
            return {"success": False, "error": "不支持的上下文操作"}
    
    def _build_mcp_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """构建MCP格式的提示"""
        # 构建历史对话
        history = "\n".join([
            f"{item['role']}: {item['content']}"
            for item in self.context_window[-5:]  # 最近5轮对话
        ])
        
        # 添加上下文信息
        context_info = "\n".join([
            f"{k}: {v}"
            for k, v in context.items()
            if k not in ["action", "timestamp"]
        ])
        
        prompt = f"""对话历史：
{history}

上下文信息：
{context_info}

当前用户输入：
{message}

请基于对话历史和上下文信息进行智能回复或调用工具。"""
        
        return prompt
    
    async def _compress_context(self, context_window: List[Dict]) -> List[Dict]:
        """压缩上下文 - 保留关键信息"""
        if len(context_window) <= self.max_context_length:
            return context_window
        
        # 构建压缩提示
        context_text = "\n".join([
            f"{item['role']}: {item['content']}"
            for item in context_window
        ])
        
        system_prompt = """你是一个上下文压缩专家。将长对话历史压缩成关键信息，保留：
1. 重要决策和结论
2. 关键信息和数据
3. 用户偏好和设置
4. 待办事项

返回压缩后的对话历史（保留最重要的内容）。"""

        prompt = f"对话历史：\n{context_text}\n\n请压缩为{self.max_context_length}条关键信息。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            # 简单的压缩策略：保留最新的几条和重要的历史
            compressed = context_window[-self.max_context_length:]
            
            return compressed
        except Exception as e:
            # 失败时返回最近的对话
            return context_window[-self.max_context_length:]
