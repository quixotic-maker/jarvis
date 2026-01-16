"""
成长追踪API端点

提供：
- 学习统计
- 成就系统
- 成长历程
- 数据分析
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.db.database import get_db
from app.api.schemas import BaseResponse

router = APIRouter()


# ==================== Pydantic Models ====================

class DailyStats(BaseModel):
    """每日统计"""
    date: date
    tasks_completed: int
    study_minutes: int
    agents_used: int
    knowledge_added: int
    
    class Config:
        from_attributes = True


class Achievement(BaseModel):
    """成就"""
    id: int
    title: str
    description: str
    icon: str
    category: str
    progress: float
    total: int
    current: int
    unlocked: bool
    unlocked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GrowthOverview(BaseModel):
    """成长概览"""
    total_days: int
    total_tasks: int
    total_study_hours: float
    total_knowledge_nodes: int
    achievements_unlocked: int
    current_streak: int
    longest_streak: int
    level: int
    level_progress: float


class ActivityHeatmap(BaseModel):
    """活动热力图数据"""
    date: date
    activity_count: int
    intensity: str  # low, medium, high


# ==================== 成长数据端点 ====================

@router.get("/overview", summary="获取成长概览")
async def get_growth_overview(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[GrowthOverview]:
    """获取用户的成长数据概览"""
    # TODO: 实现真实的数据库查询
    overview = {
        "total_days": 45,
        "total_tasks": 237,
        "total_study_hours": 68.5,
        "total_knowledge_nodes": 42,
        "achievements_unlocked": 12,
        "current_streak": 7,
        "longest_streak": 15,
        "level": 5,
        "level_progress": 67.3,
    }
    
    return BaseResponse(
        success=True,
        data=overview
    )


@router.get("/daily-stats", summary="获取每日统计")
async def get_daily_stats(
    user_id: str = Query(default="default_user"),
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[DailyStats]]:
    """
    获取每日统计数据
    
    默认返回最近30天的数据
    """
    # TODO: 实现真实的数据库查询
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=29)
    
    # 生成模拟数据
    stats = []
    current_date = start_date
    while current_date <= end_date:
        stats.append({
            "date": current_date,
            "tasks_completed": (current_date.day * 7) % 12 + 1,
            "study_minutes": (current_date.day * 13) % 180 + 30,
            "agents_used": (current_date.day * 5) % 8 + 2,
            "knowledge_added": (current_date.day * 3) % 5,
        })
        current_date += timedelta(days=1)
    
    return BaseResponse(
        success=True,
        data=stats
    )


@router.get("/achievements", summary="获取成就列表")
async def get_achievements(
    user_id: str = Query(default="default_user"),
    category: Optional[str] = Query(default=None, description="成就分类"),
    unlocked_only: bool = Query(default=False, description="只显示已解锁"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[Achievement]]:
    """获取用户的成就列表"""
    # TODO: 实现真实的数据库查询
    achievements = [
        {
            "id": 1,
            "title": "坚持学习7天",
            "description": "连续7天完成学习任务",
            "icon": "award",
            "category": "streak",
            "progress": 100.0,
            "total": 7,
            "current": 7,
            "unlocked": True,
            "unlocked_at": datetime.now() - timedelta(days=3),
        },
        {
            "id": 2,
            "title": "完成10个任务",
            "description": "累计完成10个待办任务",
            "icon": "check-circle",
            "category": "task",
            "progress": 100.0,
            "total": 10,
            "current": 10,
            "unlocked": True,
            "unlocked_at": datetime.now() - timedelta(days=10),
        },
        {
            "id": 3,
            "title": "学习100小时",
            "description": "累计学习时长达到100小时",
            "icon": "clock",
            "category": "study",
            "progress": 68.5,
            "total": 100,
            "current": 68,
            "unlocked": False,
            "unlocked_at": None,
        },
        {
            "id": 4,
            "title": "知识大师",
            "description": "创建50个知识节点",
            "icon": "brain",
            "category": "knowledge",
            "progress": 84.0,
            "total": 50,
            "current": 42,
            "unlocked": False,
            "unlocked_at": None,
        },
        {
            "id": 5,
            "title": "早起鸟",
            "description": "早上7点前完成5次任务",
            "icon": "sunrise",
            "category": "habit",
            "progress": 60.0,
            "total": 5,
            "current": 3,
            "unlocked": False,
            "unlocked_at": None,
        },
        {
            "id": 6,
            "title": "效率达人",
            "description": "单日完成15个任务",
            "icon": "zap",
            "category": "task",
            "progress": 100.0,
            "total": 15,
            "current": 15,
            "unlocked": True,
            "unlocked_at": datetime.now() - timedelta(days=5),
        },
    ]
    
    # 按分类筛选
    if category:
        achievements = [a for a in achievements if a["category"] == category]
    
    # 只显示已解锁
    if unlocked_only:
        achievements = [a for a in achievements if a["unlocked"]]
    
    return BaseResponse(
        success=True,
        data=achievements
    )


@router.get("/activity-heatmap", summary="获取活动热力图数据")
async def get_activity_heatmap(
    user_id: str = Query(default="default_user"),
    year: int = Query(default=2026, description="年份"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[ActivityHeatmap]]:
    """
    获取活动热力图数据（类似GitHub贡献图）
    
    返回指定年份每天的活动强度
    """
    # TODO: 实现真实的数据库查询
    heatmap_data = []
    start_date = date(year, 1, 1)
    end_date = date.today() if year == date.today().year else date(year, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        activity_count = (current_date.day * current_date.month * 3) % 20
        
        # 确定强度
        if activity_count == 0:
            intensity = "none"
        elif activity_count < 5:
            intensity = "low"
        elif activity_count < 12:
            intensity = "medium"
        else:
            intensity = "high"
        
        heatmap_data.append({
            "date": current_date,
            "activity_count": activity_count,
            "intensity": intensity,
        })
        current_date += timedelta(days=1)
    
    return BaseResponse(
        success=True,
        data=heatmap_data
    )


@router.get("/streak", summary="获取连续打卡信息")
async def get_streak_info(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[dict]:
    """获取用户的连续打卡信息"""
    # TODO: 实现真实的数据库查询
    streak_info = {
        "current_streak": 7,
        "longest_streak": 15,
        "total_check_ins": 45,
        "last_check_in": date.today().isoformat(),
        "streak_history": [
            {"start_date": "2026-01-09", "end_date": "2026-01-15", "days": 7},
            {"start_date": "2025-12-20", "end_date": "2026-01-03", "days": 15},
        ],
    }
    
    return BaseResponse(
        success=True,
        data=streak_info
    )


@router.post("/check-in", summary="每日打卡")
async def daily_check_in(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[dict]:
    """用户每日打卡"""
    # TODO: 实现真实的数据库创建
    result = {
        "checked_in": True,
        "streak": 8,
        "reward": "连续打卡8天，获得10经验值！",
        "next_milestone": {
            "days": 10,
            "reward": "坚持学习10天成就",
        },
    }
    
    return BaseResponse(
        success=True,
        message="打卡成功！",
        data=result
    )
