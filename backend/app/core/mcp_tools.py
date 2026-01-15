"""
MCP (Model Context Protocol) 工具框架
提供文件系统、数据库、浏览器等工具能力
"""
import os
import json
import glob
import asyncio
import aiohttp
import aiofiles
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path
from enum import Enum

from app.core.config import settings


class MCPToolStatus(Enum):
    """工具执行状态"""
    SUCCESS = "success"
    ERROR = "error"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"


class MCPToolResult:
    """MCP工具执行结果"""
    
    def __init__(
        self, 
        status: MCPToolStatus, 
        data: Any = None, 
        message: str = "",
        metadata: Dict[str, Any] = None
    ):
        self.status = status
        self.data = data
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    @property
    def is_success(self) -> bool:
        return self.status == MCPToolStatus.SUCCESS


class MCPTool(ABC):
    """MCP工具基类"""
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.parameters: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> MCPToolResult:
        """执行工具"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的JSON Schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


# ============== 文件系统工具 ==============

class FileReadTool(MCPTool):
    """读取文件内容"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_read"
        self.description = "读取文件内容"
        self.parameters = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "encoding": {"type": "string", "default": "utf-8"},
            },
            "required": ["path"],
        }
    
    async def execute(self, path: str, encoding: str = "utf-8") -> MCPToolResult:
        try:
            # 安全检查
            abs_path = os.path.abspath(path)
            if not self._is_safe_path(abs_path):
                return MCPToolResult(
                    MCPToolStatus.PERMISSION_DENIED,
                    message="访问路径不安全"
                )
            
            if not os.path.exists(abs_path):
                return MCPToolResult(
                    MCPToolStatus.NOT_FOUND,
                    message=f"文件不存在: {path}"
                )
            
            async with aiofiles.open(abs_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                data=content,
                metadata={"path": abs_path, "size": len(content)}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )
    
    def _is_safe_path(self, path: str) -> bool:
        """检查路径安全性"""
        # 禁止访问系统敏感目录
        forbidden = ["/etc", "/root", "/sys", "/proc", "/boot"]
        for f in forbidden:
            if path.startswith(f):
                return False
        return True


class FileWriteTool(MCPTool):
    """写入文件内容"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_write"
        self.description = "写入内容到文件"
        self.parameters = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "写入内容"},
                "mode": {"type": "string", "enum": ["write", "append"], "default": "write"},
            },
            "required": ["path", "content"],
        }
    
    async def execute(
        self, 
        path: str, 
        content: str, 
        mode: str = "write"
    ) -> MCPToolResult:
        try:
            abs_path = os.path.abspath(path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            file_mode = 'w' if mode == "write" else 'a'
            async with aiofiles.open(abs_path, file_mode, encoding='utf-8') as f:
                await f.write(content)
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                message=f"文件已{'写入' if mode == 'write' else '追加'}",
                metadata={"path": abs_path, "size": len(content)}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


class FileSearchTool(MCPTool):
    """搜索文件"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_search"
        self.description = "搜索文件"
        self.parameters = {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "搜索目录"},
                "pattern": {"type": "string", "description": "搜索模式(glob)"},
                "recursive": {"type": "boolean", "default": True},
            },
            "required": ["directory", "pattern"],
        }
    
    async def execute(
        self, 
        directory: str, 
        pattern: str, 
        recursive: bool = True
    ) -> MCPToolResult:
        try:
            abs_dir = os.path.abspath(directory)
            if not os.path.isdir(abs_dir):
                return MCPToolResult(
                    MCPToolStatus.NOT_FOUND,
                    message=f"目录不存在: {directory}"
                )
            
            if recursive:
                search_pattern = os.path.join(abs_dir, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(abs_dir, pattern)
                files = glob.glob(search_pattern)
            
            file_info = []
            for f in files[:100]:  # 限制返回数量
                stat = os.stat(f)
                file_info.append({
                    "path": f,
                    "name": os.path.basename(f),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                data=file_info,
                metadata={"total": len(files), "returned": len(file_info)}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


class FileListTool(MCPTool):
    """列出目录内容"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_list"
        self.description = "列出目录内容"
        self.parameters = {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "目录路径"},
            },
            "required": ["directory"],
        }
    
    async def execute(self, directory: str) -> MCPToolResult:
        try:
            abs_dir = os.path.abspath(directory)
            if not os.path.isdir(abs_dir):
                return MCPToolResult(
                    MCPToolStatus.NOT_FOUND,
                    message=f"目录不存在: {directory}"
                )
            
            items = []
            for item in os.listdir(abs_dir):
                item_path = os.path.join(abs_dir, item)
                stat = os.stat(item_path)
                items.append({
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                data=items,
                metadata={"directory": abs_dir, "count": len(items)}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


# ============== 网络请求工具 ==============

class HttpRequestTool(MCPTool):
    """HTTP请求工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "http_request"
        self.description = "发送HTTP请求"
        self.parameters = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "请求URL"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                "headers": {"type": "object", "description": "请求头"},
                "body": {"type": "object", "description": "请求体"},
            },
            "required": ["url"],
        }
    
    async def execute(
        self, 
        url: str, 
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: Dict[str, Any] = None
    ) -> MCPToolResult:
        try:
            async with aiohttp.ClientSession() as session:
                kwargs = {"headers": headers or {}}
                if body:
                    kwargs["json"] = body
                
                async with session.request(method, url, **kwargs) as response:
                    content_type = response.headers.get("Content-Type", "")
                    
                    if "application/json" in content_type:
                        data = await response.json()
                    else:
                        data = await response.text()
                    
                    return MCPToolResult(
                        MCPToolStatus.SUCCESS,
                        data=data,
                        metadata={
                            "status_code": response.status,
                            "headers": dict(response.headers),
                        }
                    )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


class WebScrapeTool(MCPTool):
    """网页抓取工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "web_scrape"
        self.description = "抓取网页内容"
        self.parameters = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "网页URL"},
                "selector": {"type": "string", "description": "CSS选择器（可选）"},
            },
            "required": ["url"],
        }
    
    async def execute(self, url: str, selector: str = None) -> MCPToolResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    # 如果有BeautifulSoup，可以解析HTML
                    # 这里简单返回原始内容
                    return MCPToolResult(
                        MCPToolStatus.SUCCESS,
                        data=html[:10000],  # 限制大小
                        metadata={
                            "url": url,
                            "content_length": len(html),
                        }
                    )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


# ============== 系统工具 ==============

class ShellCommandTool(MCPTool):
    """执行Shell命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "shell_command"
        self.description = "执行Shell命令（仅限安全命令）"
        self.parameters = {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的命令"},
                "cwd": {"type": "string", "description": "工作目录"},
            },
            "required": ["command"],
        }
        
        # 允许的命令白名单
        self.allowed_commands = [
            "ls", "cat", "head", "tail", "grep", "find", "wc",
            "date", "whoami", "pwd", "echo", "df", "du",
            "python", "pip", "node", "npm", "git",
        ]
    
    async def execute(self, command: str, cwd: str = None) -> MCPToolResult:
        try:
            # 安全检查
            cmd_parts = command.split()
            if not cmd_parts:
                return MCPToolResult(
                    MCPToolStatus.ERROR,
                    message="空命令"
                )
            
            base_cmd = cmd_parts[0]
            if base_cmd not in self.allowed_commands:
                return MCPToolResult(
                    MCPToolStatus.PERMISSION_DENIED,
                    message=f"命令 '{base_cmd}' 不在允许列表中"
                )
            
            # 危险字符检查
            dangerous = [";", "&", "|", ">", "<", "`", "$", "(", ")"]
            for char in dangerous:
                if char in command:
                    return MCPToolResult(
                        MCPToolStatus.PERMISSION_DENIED,
                        message=f"命令包含不允许的字符: {char}"
                    )
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                data={
                    "stdout": stdout.decode()[:5000],  # 限制输出大小
                    "stderr": stderr.decode()[:1000],
                    "returncode": process.returncode,
                },
                metadata={"command": command}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


# ============== 数据库工具 ==============

class DatabaseQueryTool(MCPTool):
    """数据库查询工具（SQLite）"""
    
    def __init__(self, db_path: str = None):
        super().__init__()
        self.name = "database_query"
        self.description = "执行SQLite数据库查询"
        self.db_path = db_path or str(settings.DATABASE_URL).replace("sqlite:///", "")
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL查询语句（只读）"},
            },
            "required": ["query"],
        }
    
    async def execute(self, query: str) -> MCPToolResult:
        import sqlite3
        
        try:
            # 安全检查：只允许SELECT
            query_upper = query.strip().upper()
            if not query_upper.startswith("SELECT"):
                return MCPToolResult(
                    MCPToolStatus.PERMISSION_DENIED,
                    message="只允许SELECT查询"
                )
            
            # 检查危险关键字
            dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
            for word in dangerous:
                if word in query_upper:
                    return MCPToolResult(
                        MCPToolStatus.PERMISSION_DENIED,
                        message=f"查询包含不允许的关键字: {word}"
                    )
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            data = [dict(row) for row in rows[:100]]  # 限制返回数量
            
            conn.close()
            
            return MCPToolResult(
                MCPToolStatus.SUCCESS,
                data=data,
                metadata={"row_count": len(data)}
            )
        except Exception as e:
            return MCPToolResult(
                MCPToolStatus.ERROR,
                message=str(e)
            )


# ============== MCP管理器 ==============

class MCPManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        default_tools = [
            FileReadTool(),
            FileWriteTool(),
            FileSearchTool(),
            FileListTool(),
            HttpRequestTool(),
            WebScrapeTool(),
            ShellCommandTool(),
            DatabaseQueryTool(),
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> MCPToolResult:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return MCPToolResult(
                MCPToolStatus.NOT_FOUND,
                message=f"工具不存在: {name}"
            )
        
        return await tool.execute(**kwargs)
    
    def get_tools_description(self) -> str:
        """获取工具描述（用于LLM）"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- **{tool.name}**: {tool.description}")
        return "\n".join(descriptions)


# 全局单例
_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """获取MCP管理器单例"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager
