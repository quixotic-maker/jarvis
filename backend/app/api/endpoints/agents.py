"""Agent相关API端点"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import AgentLog
from app.agents import AGENT_REGISTRY
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


class AgentInfo(BaseModel):
    """Agent信息模型"""
    name: str
    description: str


class AgentLogResponse(BaseModel):
    """Agent日志响应模型"""
    id: int
    agent_name: str
    task_id: int | None
    action: str
    execution_time: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AgentInfo])
async def get_agents():
    """获取所有可用的Agent列表"""
    agents = []
    for name, agent_class in AGENT_REGISTRY.items():
        agent = agent_class()
        agents.append({
            "name": agent.name,
            "description": agent.description
        })
    return agents


@router.get("/logs", response_model=List[AgentLogResponse])
async def get_agent_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取Agent执行日志"""
    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/{agent_name}/logs", response_model=List[AgentLogResponse])
async def get_agent_logs_by_name(agent_name: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取特定Agent的执行日志"""
    logs = db.query(AgentLog).filter(
        AgentLog.agent_name == agent_name
    ).order_by(AgentLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs
