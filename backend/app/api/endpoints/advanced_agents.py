"""高级Agent API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db.database import get_db
from app.agents import get_agent

router = APIRouter()


@router.post("/knowledge-graph/extract")
async def extract_knowledge(
    text: str,
    db: Session = Depends(get_db)
):
    """从文本中提取知识图谱"""
    try:
        agent = get_agent("KnowledgeGraphAgent")()
        result = await agent.execute({
            "action": "extract",
            "user_input": text,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-graph/query")
async def query_knowledge_graph(
    query: str,
    db: Session = Depends(get_db)
):
    """查询知识图谱"""
    try:
        agent = get_agent("KnowledgeGraphAgent")()
        result = await agent.execute({
            "action": "query",
            "user_input": query,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-graph/build")
async def build_knowledge_graph(
    topic: str,
    db: Session = Depends(get_db)
):
    """根据主题构建知识图谱"""
    try:
        agent = get_agent("KnowledgeGraphAgent")()
        result = await agent.execute({
            "action": "build",
            "user_input": topic,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/index")
async def index_document(
    document: str,
    db: Session = Depends(get_db)
):
    """索引文档到RAG系统"""
    try:
        agent = get_agent("RAGAgent")()
        result = await agent.execute({
            "action": "index",
            "user_input": document,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/query")
async def rag_query(
    query: str,
    db: Session = Depends(get_db)
):
    """RAG检索增强查询"""
    try:
        agent = get_agent("RAGAgent")()
        result = await agent.execute({
            "action": "query",
            "user_input": query,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agentic-rag/query")
async def agentic_rag_query(
    query: str,
    max_iterations: int = 3,
    db: Session = Depends(get_db)
):
    """Agentic RAG高级查询"""
    try:
        agent = get_agent("AgenticRAGAgent")()
        result = await agent.execute({
            "user_input": query,
            "max_iterations": max_iterations,
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/chat")
async def mcp_chat(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """MCP对话"""
    try:
        agent = get_agent("MCPAgent")()
        result = await agent.execute({
            "action": "chat",
            "user_input": message,
            "context": context or {},
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/tool-call")
async def mcp_tool_call(
    tool_request: str,
    context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """MCP工具调用"""
    try:
        agent = get_agent("MCPAgent")()
        result = await agent.execute({
            "action": "tool_call",
            "user_input": tool_request,
            "context": context or {},
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/context")
async def get_mcp_context(
    db: Session = Depends(get_db)
):
    """获取MCP上下文"""
    try:
        agent = get_agent("MCPAgent")()
        result = await agent.execute({
            "action": "context_manage",
            "context": {"action": "get"},
            "db": db
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
