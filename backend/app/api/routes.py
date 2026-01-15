"""API路由"""
from fastapi import APIRouter

from app.api.endpoints import tasks, schedules, agents, reminders, advanced_agents, chat

api_router = APIRouter()

# 核心对话API（最重要）
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# 其他端点路由
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(advanced_agents.router, prefix="/advanced", tags=["advanced-agents"])

