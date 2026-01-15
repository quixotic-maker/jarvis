"""
对话API端点 - Jarvis核心对话接口

提供：
- 对话消息处理（支持流式输出）
- 会话管理
- 用户记忆管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
import json
import asyncio

from app.db.database import get_db
from app.core.chat_service import ChatService, ChatResponse
from app.core.memory import MemoryManager

router = APIRouter()


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，不传则创建新会话")
    user_id: str = Field(default="default_user", description="用户ID")


class ChatResponseModel(BaseModel):
    """对话响应"""
    session_id: str
    message_id: int
    content: str
    intent: str
    intent_confidence: float
    agent_used: Optional[str] = None
    action_result: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    emotion_detected: Optional[str] = None
    response_time_ms: int


class SessionModel(BaseModel):
    """会话模型"""
    id: str
    user_id: str
    title: Optional[str]
    summary: Optional[str]
    is_active: bool
    message_count: int
    last_activity: datetime
    created_at: datetime


class MessageModel(BaseModel):
    """消息模型"""
    id: int
    session_id: str
    role: str
    content: str
    intent: Optional[str]
    agent_used: Optional[str]
    emotion: Optional[str]
    created_at: datetime


class UserProfileUpdate(BaseModel):
    """用户档案更新"""
    name: Optional[str] = None
    nickname: Optional[str] = None
    occupation: Optional[str] = None
    company: Optional[str] = None
    communication_style: Optional[str] = None
    response_length: Optional[str] = None
    interests: Optional[List[str]] = None


class RelationshipCreate(BaseModel):
    """创建关系"""
    person_name: str
    relationship_type: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None


class MemoryCreate(BaseModel):
    """创建记忆"""
    content: str
    memory_type: str = "episode"
    importance: float = 0.5
    tags: Optional[List[str]] = None


# ==================== 对话端点 ====================

@router.post("/chat", response_model=ChatResponseModel, summary="发送消息")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    发送消息并获取Jarvis回复
    
    这是Jarvis的核心对话接口，支持：
    - 自然语言理解
    - 意图识别
    - 自动调用对应Agent
    - 上下文记忆
    """
    chat_service = ChatService(db)
    
    try:
        response = await chat_service.chat(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponseModel(
            session_id=response.session_id,
            message_id=response.message_id,
            content=response.content,
            intent=response.intent,
            intent_confidence=response.intent_confidence,
            agent_used=response.agent_used,
            action_result=response.action_result,
            suggestions=response.suggestions,
            emotion_detected=response.emotion_detected,
            response_time_ms=response.response_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream", summary="流式对话")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    流式对话接口 - 实时返回AI响应
    
    使用Server-Sent Events (SSE)实现流式输出
    """
    chat_service = ChatService(db)
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'session_id': None})}\n\n"
            
            # 获取流式响应
            async for chunk in chat_service.chat_stream(
                user_id=request.user_id,
                message=request.message,
                session_id=request.session_id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/quick", summary="快速对话（无会话）")
async def quick_chat(
    message: str = Query(..., description="用户消息"),
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """快速对话，不保存会话历史"""
    chat_service = ChatService(db)
    
    try:
        response = await chat_service.chat(
            user_id=user_id,
            message=message,
            session_id=None
        )
        
        return {
            "content": response.content,
            "intent": response.intent,
            "agent_used": response.agent_used
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/greeting", summary="获取主动问候")
async def get_greeting(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """
    获取基于时间和上下文的主动问候
    
    返回：
    - 时间问候语
    - 今日概览（日程、待办、天气）
    - 推荐的快捷操作
    """
    from app.core.persona_engine import get_persona_engine
    
    persona = get_persona_engine()
    
    # 获取问候语
    greeting = persona.get_greeting(is_first_interaction=True)
    
    # 获取快捷操作
    quick_actions = persona.get_quick_actions()
    
    # 获取时间段信息
    time_of_day = persona.get_time_of_day().value
    
    return {
        "greeting": greeting,
        "time_of_day": time_of_day,
        "quick_actions": quick_actions,
        "proactive_message": persona.get_proactive_message({})
    }


@router.get("/mcp/tools", summary="获取可用的MCP工具")
async def get_mcp_tools():
    """获取所有可用的MCP工具列表"""
    from app.core.mcp_tools import get_mcp_manager
    
    mcp = get_mcp_manager()
    return {
        "tools": mcp.list_tools(),
        "description": mcp.get_tools_description()
    }


@router.post("/mcp/execute", summary="执行MCP工具")
async def execute_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """直接执行MCP工具"""
    from app.core.mcp_tools import get_mcp_manager
    
    mcp = get_mcp_manager()
    result = await mcp.execute_tool(tool_name, **arguments)
    
    return result.to_dict()


# ==================== 会话管理端点 ====================

@router.get("/sessions", response_model=List[SessionModel], summary="获取会话列表")
async def get_sessions(
    user_id: str = Query(default="default_user"),
    limit: int = Query(default=20, le=100),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """获取用户的会话列表"""
    chat_service = ChatService(db)
    
    sessions = await chat_service.get_sessions(
        user_id=user_id,
        limit=limit,
        include_inactive=include_inactive
    )
    
    return [
        SessionModel(
            id=s.id,
            user_id=s.user_id,
            title=s.title,
            summary=s.summary,
            is_active=s.is_active,
            message_count=s.message_count,
            last_activity=s.last_activity,
            created_at=s.created_at
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=List[MessageModel], summary="获取会话消息")
async def get_session_messages(
    session_id: str,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """获取会话的消息历史"""
    chat_service = ChatService(db)
    
    messages = await chat_service.get_session_messages(session_id, limit)
    
    return [
        MessageModel(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            intent=m.intent,
            agent_used=m.agent_used,
            emotion=m.emotion,
            created_at=m.created_at
        )
        for m in messages
    ]


@router.delete("/sessions/{session_id}", summary="删除会话")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """删除指定会话"""
    chat_service = ChatService(db)
    
    success = await chat_service.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True, "message": "Session deleted"}


# ==================== 用户档案端点 ====================

@router.get("/profile", summary="获取用户档案")
async def get_profile(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """获取用户档案信息"""
    memory_manager = MemoryManager(db)
    
    profile = await memory_manager.get_profile_summary(user_id)
    return profile


@router.put("/profile", summary="更新用户档案")
async def update_profile(
    updates: UserProfileUpdate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """更新用户档案"""
    memory_manager = MemoryManager(db)
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    profile = await memory_manager.update_profile(user_id, update_dict)
    
    return {"success": True, "message": "Profile updated"}


# ==================== 关系图谱端点 ====================

@router.get("/relationships", summary="获取关系列表")
async def get_relationships(
    user_id: str = Query(default="default_user"),
    relationship_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """获取用户的关系图谱"""
    memory_manager = MemoryManager(db)
    
    relationships = await memory_manager.get_relationships(user_id, relationship_type)
    
    return [
        {
            "id": r.id,
            "person_name": r.person_name,
            "relationship_type": r.relationship_type,
            "phone": r.phone,
            "email": r.email,
            "company": r.company,
            "position": r.position,
            "importance": r.importance,
            "mention_count": r.mention_count,
            "notes": r.notes
        }
        for r in relationships
    ]


@router.post("/relationships", summary="添加关系")
async def add_relationship(
    relationship: RelationshipCreate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """添加新的关系人"""
    memory_manager = MemoryManager(db)
    
    result = await memory_manager.add_relationship(
        user_id=user_id,
        person_name=relationship.person_name,
        relationship_type=relationship.relationship_type,
        phone=relationship.phone,
        email=relationship.email,
        company=relationship.company,
        position=relationship.position,
        notes=relationship.notes
    )
    
    return {
        "success": True,
        "relationship_id": result.id,
        "message": f"Added relationship: {relationship.person_name}"
    }


# ==================== 记忆管理端点 ====================

@router.get("/memories", summary="获取记忆")
async def get_memories(
    user_id: str = Query(default="default_user"),
    query: Optional[str] = Query(default=None, description="搜索关键词"),
    memory_type: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """搜索用户记忆"""
    memory_manager = MemoryManager(db)
    
    memories = await memory_manager.search_memories(
        user_id=user_id,
        query=query,
        memory_type=memory_type,
        limit=limit
    )
    
    return [
        {
            "id": m.id,
            "memory_type": m.memory_type,
            "content": m.content,
            "summary": m.summary,
            "importance": m.importance,
            "tags": m.tags,
            "created_at": m.created_at
        }
        for m in memories
    ]


@router.post("/memories", summary="添加记忆")
async def add_memory(
    memory: MemoryCreate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """手动添加记忆"""
    memory_manager = MemoryManager(db)
    
    result = await memory_manager.store_memory(
        user_id=user_id,
        content=memory.content,
        memory_type=memory.memory_type,
        importance=memory.importance,
        tags=memory.tags
    )
    
    return {
        "success": True,
        "memory_id": result.id,
        "message": "Memory stored"
    }


# ==================== 偏好设置端点 ====================

@router.get("/preferences", summary="获取偏好设置")
async def get_preferences(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """获取用户的所有偏好设置"""
    memory_manager = MemoryManager(db)
    
    preferences = await memory_manager.get_all_preferences(user_id)
    return preferences


@router.put("/preferences/{category}/{key}", summary="设置偏好")
async def set_preference(
    category: str,
    key: str,
    value: Any,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
):
    """设置用户偏好"""
    memory_manager = MemoryManager(db)
    
    await memory_manager.set_preference(
        user_id=user_id,
        category=category,
        key=key,
        value=value,
        source="explicit"
    )
    
    return {"success": True, "message": f"Preference {category}.{key} updated"}


# ==================== 上下文端点 ====================

@router.get("/context", summary="获取完整上下文")
async def get_full_context(
    user_id: str = Query(default="default_user"),
    current_query: str = Query(default=""),
    db: Session = Depends(get_db)
):
    """获取用户的完整上下文（用于调试）"""
    memory_manager = MemoryManager(db)
    
    context = await memory_manager.get_full_context(user_id, current_query)
    return context
