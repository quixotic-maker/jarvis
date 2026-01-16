"""API路由"""
from fastapi import APIRouter

from app.api.endpoints import (
    tasks, 
    schedules, 
    agents, 
    reminders, 
    advanced_agents, 
    chat,
    settings,
    learning
)
from app.api.endpoints import tasks_v2  # 新版tasks API

api_router = APIRouter()

# 核心对话API（最重要）
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# V2版本API（使用统一响应格式）
api_router.include_router(tasks_v2.router, prefix="/v2/tasks", tags=["tasks-v2"])
api_router.include_router(schedules.router, prefix="/v2/schedules", tags=["schedules-v2"])
api_router.include_router(settings.router, prefix="/v2/settings", tags=["settings-v2"])
api_router.include_router(learning.router, prefix="/v2/learning", tags=["learning-v2"])

# 其他端点路由（保留旧版兼容）
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules-legacy"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(advanced_agents.router, prefix="/advanced", tags=["advanced-agents"])


