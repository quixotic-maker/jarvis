"""MCP (Model Context Protocol) Agent - 模型上下文协议 & 工具调用"""
from typing import Dict, Any, List, Optional
import json
import re

from app.agents.base_agent import BaseAgent
from app.core.mcp_tools import get_mcp_manager, MCPToolResult, MCPToolStatus


class MCPAgent(BaseAgent):
    """
    MCP Agent - 模型上下文协议Agent
    
    实现标准化的模型上下文管理和工具调用：
    1. 上下文管理 - 智能管理对话上下文
    2. MCP工具调用 - 文件系统、数据库、网络等
    3. 状态保持 - 维护对话状态和历史
    4. 工具链 - 支持多工具连续调用
    """
    
    def __init__(self):
        super().__init__(
            name="MCPAgent",
            description="MCP工具调用Agent，可执行文件操作、网络请求、数据库查询等"
        )
        self.context_window = []
        self.max_context_length = 10
        self.mcp = get_mcp_manager()
    
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
        elif action == "execute_tool":
            return await self._execute_mcp_tool(user_input, context)
        elif action == "list_tools":
            return await self._list_mcp_tools()
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _execute_mcp_tool(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行MCP工具 - 智能解析用户意图并调用工具"""
        # 分析应该调用哪个工具
        tool_call = await self._analyze_tool_call(message, context)
        
        if not tool_call or not tool_call.get("tool"):
            return {
                "success": False,
                "message": "抱歉，我不确定你想要执行什么操作。可以更具体地描述一下吗？",
                "available_tools": self.mcp.list_tools(),
            }
        
        # 执行工具
        tool_name = tool_call.get("tool")
        tool_args = tool_call.get("arguments", {})
        
        result = await self.mcp.execute_tool(tool_name, **tool_args)
        
        # 格式化结果
        formatted = self._format_tool_result(tool_name, result)
        
        return {
            "success": result.is_success,
            "tool_used": tool_name,
            "result": result.to_dict(),
            "message": formatted,
        }
    
    async def _analyze_tool_call(self, message: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用LLM分析应该调用哪个工具"""
        tools_desc = self.mcp.get_tools_description()
        tools_list = self.mcp.list_tools()
        
        system_prompt = f"""你是一个工具调用分析器。根据用户的请求，判断应该使用哪个工具以及参数。

可用的工具:
{tools_desc}

工具详细参数:
{json.dumps(tools_list, ensure_ascii=False, indent=2)}

请分析用户意图，返回JSON格式的工具调用:
{{
    "tool": "工具名称",
    "arguments": {{
        "参数名": "参数值"
    }},
    "reasoning": "选择这个工具的原因"
}}

如果无法确定应该使用哪个工具，返回:
{{
    "tool": null,
    "reasoning": "原因"
}}

只返回JSON，不要其他内容。"""
        
        prompt = f"用户请求: {message}"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            
            # 清理响应，提取JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            
            result = json.loads(response.strip())
            
            if result.get("tool"):
                return result
            return None
            
        except Exception as e:
            print(f"分析工具调用失败: {e}")
            # 简单的关键词匹配作为后备
            return self._keyword_match(message)
    
    def _keyword_match(self, message: str) -> Optional[Dict[str, Any]]:
        """简单的关键词匹配（作为LLM分析的后备）"""
        message_lower = message.lower()
        
        # 文件相关
        if any(kw in message_lower for kw in ["读取文件", "查看文件", "打开文件", "读文件"]):
            paths = re.findall(r'[\'"]?([/\w\.\-_]+\.\w+)[\'"]?', message)
            if paths:
                return {"tool": "file_read", "arguments": {"path": paths[0]}}
        
        if any(kw in message_lower for kw in ["列出目录", "目录内容", "文件列表", "ls"]):
            paths = re.findall(r'[\'"]?(/[\w\.\-_/]+)[\'"]?', message)
            return {"tool": "file_list", "arguments": {"directory": paths[0] if paths else "."}}
        
        if any(kw in message_lower for kw in ["搜索文件", "查找文件", "找文件"]):
            return {"tool": "file_search", "arguments": {"directory": ".", "pattern": "*"}}
        
        # 网络请求
        if any(kw in message_lower for kw in ["访问网页", "抓取网页", "获取网页"]):
            urls = re.findall(r'https?://[^\s]+', message)
            if urls:
                return {"tool": "web_scrape", "arguments": {"url": urls[0]}}
        
        # 数据库
        if any(kw in message_lower for kw in ["查询数据", "数据库", "sql"]):
            return {"tool": "database_query", "arguments": {"query": "SELECT * FROM sqlite_master WHERE type='table'"}}
        
        return None
    
    def _format_tool_result(self, tool_name: str, result: MCPToolResult) -> str:
        """格式化工具执行结果"""
        if not result.is_success:
            return f"❌ 执行失败: {result.message}"
        
        formatters = {
            "file_read": self._format_file_read,
            "file_list": self._format_file_list,
            "file_search": self._format_file_search,
            "file_write": self._format_file_write,
            "http_request": self._format_http,
            "web_scrape": self._format_web_scrape,
            "shell_command": self._format_shell,
            "database_query": self._format_database,
        }
        
        formatter = formatters.get(tool_name, self._format_default)
        return formatter(result)
    
    def _format_file_read(self, result: MCPToolResult) -> str:
        content = result.data
        path = result.metadata.get("path", "")
        size = result.metadata.get("size", 0)
        
        if len(content) > 2000:
            content = content[:2000] + f"\n\n... (内容过长，已截断，共 {size} 字符)"
        
        return f"""📄 **文件内容** ({path})

```
{content}
```"""
    
    def _format_file_list(self, result: MCPToolResult) -> str:
        items = result.data
        directory = result.metadata.get("directory", "")
        
        if not items:
            return f"📁 目录 `{directory}` 为空"
        
        lines = [f"📁 **目录内容** ({directory})\n"]
        lines.append("| 类型 | 名称 | 大小 | 修改时间 |")
        lines.append("|------|------|------|----------|")
        
        for item in items[:20]:
            icon = "📁" if item["type"] == "directory" else "📄"
            size = self._format_size(item["size"])
            modified = item["modified"][:10]
            lines.append(f"| {icon} | {item['name']} | {size} | {modified} |")
        
        if len(items) > 20:
            lines.append(f"\n... 还有 {len(items) - 20} 个项目")
        
        return "\n".join(lines)
    
    def _format_file_search(self, result: MCPToolResult) -> str:
        files = result.data
        total = result.metadata.get("total", 0)
        
        if not files:
            return "🔍 没有找到匹配的文件"
        
        lines = [f"🔍 **搜索结果** (共 {total} 个文件)\n"]
        
        for f in files[:10]:
            size = self._format_size(f["size"])
            lines.append(f"- `{f['path']}` ({size})")
        
        if total > 10:
            lines.append(f"\n... 还有 {total - 10} 个文件")
        
        return "\n".join(lines)
    
    def _format_file_write(self, result: MCPToolResult) -> str:
        path = result.metadata.get("path", "")
        size = result.metadata.get("size", 0)
        return f"✅ 文件已保存到 `{path}` ({size} 字符)"
    
    def _format_http(self, result: MCPToolResult) -> str:
        status_code = result.metadata.get("status_code", 0)
        data = result.data
        
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False, indent=2)[:1500]
        else:
            data_str = str(data)[:1500]
        
        return f"""🌐 **HTTP响应** (状态码: {status_code})

```json
{data_str}
```"""
    
    def _format_web_scrape(self, result: MCPToolResult) -> str:
        url = result.metadata.get("url", "")
        content_length = result.metadata.get("content_length", 0)
        
        return f"""🌐 **网页内容** ({url})

内容长度: {content_length} 字符

*提示: 完整内容可以让我帮你分析或提取特定信息*"""
    
    def _format_shell(self, result: MCPToolResult) -> str:
        data = result.data
        command = result.metadata.get("command", "")
        
        output = data.get("stdout", "")
        error = data.get("stderr", "")
        returncode = data.get("returncode", 0)
        
        lines = [f"💻 **命令执行结果** (`{command}`)\n"]
        
        if output:
            lines.append(f"```\n{output}\n```")
        
        if error:
            lines.append(f"\n⚠️ 错误输出:\n```\n{error}\n```")
        
        lines.append(f"\n返回码: {returncode}")
        
        return "\n".join(lines)
    
    def _format_database(self, result: MCPToolResult) -> str:
        data = result.data
        row_count = result.metadata.get("row_count", 0)
        
        if not data:
            return "📊 查询结果为空"
        
        columns = list(data[0].keys())
        
        lines = [f"📊 **查询结果** ({row_count} 行)\n"]
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        
        for row in data[:20]:
            values = [str(row.get(col, ""))[:30] for col in columns]
            lines.append("| " + " | ".join(values) + " |")
        
        if row_count > 20:
            lines.append(f"\n... 还有 {row_count - 20} 行")
        
        return "\n".join(lines)
    
    def _format_default(self, result: MCPToolResult) -> str:
        return f"✅ 操作完成\n\n```json\n{json.dumps(result.data, ensure_ascii=False, indent=2)[:1000]}\n```"
    
    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/1024/1024:.1f}MB"
    
    async def _list_mcp_tools(self) -> Dict[str, Any]:
        """列出所有可用的MCP工具"""
        return {
            "success": True,
            "tools": self.mcp.list_tools(),
            "description": self.mcp.get_tools_description(),
        }
    
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
