"""用户设置相关API端点"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db.database import get_db
from app.api.schemas import (
    BaseResponse,
    UserSettings,
    SettingsResponse,
    SystemPreferences,
    AgentPreferences
)
from app.api.utils import success_response


router = APIRouter()


# 模拟的设置存储（实际应该存储在数据库中）
# 这里简化处理，后续可以创建Settings表
_settings_storage = {}


def get_default_settings() -> UserSettings:
    """获取默认设置"""
    return UserSettings(
        system=SystemPreferences(
            theme="dark",
            language="zh-CN",
            font_size="medium",
            sound_enabled=True,
            notifications_enabled=True,
            auto_save=True
        ),
        agent=AgentPreferences(
            default_agent="coordinator",
            response_speed="balanced",
            creativity=70,
            max_tokens=2000,
            temperature=0.7,
            enable_voice=True,
            enable_memory=True
        )
    )


@router.get("/", response_model=BaseResponse[SettingsResponse])
async def get_settings(
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取用户设置
    
    - 包括系统偏好和Agent配置
    - 如果用户没有设置，返回默认值
    """
    # 从存储中获取设置，如果不存在则返回默认值
    if user_id not in _settings_storage:
        settings = get_default_settings()
    else:
        settings = _settings_storage[user_id]
    
    response = SettingsResponse(
        user_id=user_id,
        settings=settings,
        updated_at=datetime.now()
    )
    
    return success_response(
        data=response,
        message="获取用户设置成功"
    )


@router.put("/", response_model=BaseResponse[SettingsResponse])
async def update_settings(
    settings_data: UserSettings,
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    更新用户设置
    
    - 支持更新系统偏好和Agent配置
    - 自动保存
    """
    # 保存到存储
    _settings_storage[user_id] = settings_data
    
    response = SettingsResponse(
        user_id=user_id,
        settings=settings_data,
        updated_at=datetime.now()
    )
    
    return success_response(
        data=response,
        message="更新用户设置成功"
    )


@router.patch("/system", response_model=BaseResponse[SettingsResponse])
async def update_system_preferences(
    system_prefs: SystemPreferences,
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    更新系统偏好设置
    
    - 只更新系统相关的设置
    - Agent配置保持不变
    """
    # 获取当前设置
    current_settings = _settings_storage.get(user_id, get_default_settings())
    
    # 更新系统偏好
    current_settings.system = system_prefs
    
    # 保存
    _settings_storage[user_id] = current_settings
    
    response = SettingsResponse(
        user_id=user_id,
        settings=current_settings,
        updated_at=datetime.now()
    )
    
    return success_response(
        data=response,
        message="更新系统偏好成功"
    )


@router.patch("/agent", response_model=BaseResponse[SettingsResponse])
async def update_agent_preferences(
    agent_prefs: AgentPreferences,
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    更新Agent配置
    
    - 只更新Agent相关的设置
    - 系统偏好保持不变
    """
    # 获取当前设置
    current_settings = _settings_storage.get(user_id, get_default_settings())
    
    # 更新Agent配置
    current_settings.agent = agent_prefs
    
    # 保存
    _settings_storage[user_id] = current_settings
    
    response = SettingsResponse(
        user_id=user_id,
        settings=current_settings,
        updated_at=datetime.now()
    )
    
    return success_response(
        data=response,
        message="更新Agent配置成功"
    )


@router.post("/reset", response_model=BaseResponse[SettingsResponse])
async def reset_settings(
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    重置为默认设置
    
    - 恢复所有设置为系统默认值
    """
    settings = get_default_settings()
    _settings_storage[user_id] = settings
    
    response = SettingsResponse(
        user_id=user_id,
        settings=settings,
        updated_at=datetime.now()
    )
    
    return success_response(
        data=response,
        message="重置设置成功"
    )
