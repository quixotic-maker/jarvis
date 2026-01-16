"""
学习工作台API端点

提供：
- 学习计划管理
- 每日任务管理
- 学习资源管理
- 学习进度跟踪
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

from app.db.database import get_db
from app.api.schemas import BaseResponse, PaginatedResponse, ResponseStatus, PaginationMeta

router = APIRouter()


# ==================== Pydantic Models ====================

class LearningPlanCreate(BaseModel):
    """创建学习计划"""
    title: str = Field(..., min_length=1, max_length=200, description="计划标题")
    goal: str = Field(..., description="学习目标")
    duration_days: int = Field(default=30, ge=1, le=365, description="计划天数")
    tags: Optional[List[str]] = Field(default=None, description="标签")


class LearningPlanUpdate(BaseModel):
    """更新学习计划"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    goal: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|paused|completed)$")


class LearningPlanResponse(BaseModel):
    """学习计划响应"""
    id: int
    user_id: str
    title: str
    goal: str
    duration_days: int
    progress: float
    status: str
    tasks_count: int
    completed_tasks_count: int
    start_date: date
    end_date: Optional[date]
    tags: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DailyTaskCreate(BaseModel):
    """创建每日任务"""
    plan_id: int = Field(..., description="所属学习计划ID")
    task_date: date = Field(..., description="任务日期")
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    task_type: str = Field(default="practice", pattern="^(reading|practice|review|project)$", description="任务类型")
    estimated_duration: Optional[int] = Field(None, ge=1, description="预计时长（分钟）")


class DailyTaskUpdate(BaseModel):
    """更新每日任务"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    actual_duration: Optional[int] = Field(None, ge=1, description="实际花费时长（分钟）")
    feedback: Optional[str] = Field(None, description="完成反馈")


class DailyTaskResponse(BaseModel):
    """每日任务响应"""
    id: int
    plan_id: int
    task_date: date
    title: str
    description: Optional[str]
    task_type: str
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    completed: bool
    feedback: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== 学习计划端点 ====================

@router.get("/plans", summary="获取学习计划列表")
async def get_learning_plans(
    user_id: str = Query(default="default_user"),
    status: Optional[str] = Query(default=None, pattern="^(active|paused|completed)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> PaginatedResponse[LearningPlanResponse]:
    """
    获取用户的学习计划列表
    
    支持按状态筛选和分页
    """
    # TODO: 实现真实的数据库查询
    # 目前返回示例数据
    demo_plans = [
        {
            "id": 1,
            "user_id": user_id,
            "title": "React高级进阶",
            "goal": "掌握React Hooks和性能优化",
            "duration_days": 30,
            "progress": 65.0,
            "status": "active",
            "tasks_count": 10,
            "completed_tasks_count": 7,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 1, 31),
            "tags": ["React", "前端", "进阶"],
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
        },
        {
            "id": 2,
            "user_id": user_id,
            "title": "TypeScript深入学习",
            "goal": "熟练使用高级类型和泛型",
            "duration_days": 45,
            "progress": 40.0,
            "status": "active",
            "tasks_count": 8,
            "completed_tasks_count": 3,
            "start_date": date(2026, 1, 10),
            "end_date": date(2026, 2, 24),
            "tags": ["TypeScript", "编程语言"],
            "created_at": datetime(2026, 1, 10, 10, 0, 0),
        },
    ]
    
    # 按状态筛选
    if status:
        demo_plans = [p for p in demo_plans if p["status"] == status]
    
    total = len(demo_plans)
    items = demo_plans[skip:skip + limit]
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        message="获取学习计划列表成功",
        data=items,
        meta=PaginationMeta(
            page=skip // limit + 1,
            page_size=limit,
            total=total,
            total_pages=total_pages
        )
    )


@router.post("/plans", summary="创建学习计划")
async def create_learning_plan(
    plan: LearningPlanCreate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[LearningPlanResponse]:
    """创建新的学习计划"""
    # TODO: 实现真实的数据库创建
    new_plan = {
        "id": 3,
        "user_id": user_id,
        "title": plan.title,
        "goal": plan.goal,
        "duration_days": plan.duration_days,
        "progress": 0.0,
        "status": "active",
        "tasks_count": 0,
        "completed_tasks_count": 0,
        "start_date": date.today(),
        "end_date": None,
        "tags": plan.tags or [],
        "created_at": datetime.now(),
    }
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习计划创建成功",
        data=new_plan
    )


@router.get("/plans/{plan_id}", summary="获取学习计划详情")
async def get_learning_plan(
    plan_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[LearningPlanResponse]:
    """获取指定学习计划的详情"""
    # TODO: 实现真实的数据库查询
    if plan_id == 1:
        plan = {
            "id": 1,
            "user_id": "default_user",
            "title": "React高级进阶",
            "goal": "掌握React Hooks和性能优化",
            "duration_days": 30,
            "progress": 65.0,
            "status": "active",
            "tasks_count": 10,
            "completed_tasks_count": 7,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 1, 31),
            "tags": ["React", "前端", "进阶"],
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
        }
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="获取学习计划成功",
            data=plan
        )
    
    raise HTTPException(status_code=404, detail="学习计划不存在")


@router.put("/plans/{plan_id}", summary="更新学习计划")
async def update_learning_plan(
    plan_id: int,
    plan: LearningPlanUpdate,
    db: Session = Depends(get_db)
) -> BaseResponse[LearningPlanResponse]:
    """更新学习计划信息"""
    # TODO: 实现真实的数据库更新
    updated_plan = {
        "id": plan_id,
        "user_id": "default_user",
        "title": plan.title or "React高级进阶",
        "goal": plan.goal or "掌握React Hooks和性能优化",
        "duration_days": 30,
        "progress": 65.0,
        "status": plan.status or "active",
        "tasks_count": 10,
        "completed_tasks_count": 7,
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 1, 31),
        "tags": ["React", "前端", "进阶"],
        "created_at": datetime(2026, 1, 1, 10, 0, 0),
    }
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习计划更新成功",
        data=updated_plan
    )


@router.delete("/plans/{plan_id}", summary="删除学习计划")
async def delete_learning_plan(
    plan_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[None]:
    """删除学习计划"""
    # TODO: 实现真实的数据库删除
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习计划删除成功",
        data=None
    )


# ==================== 每日任务端点 ====================

@router.get("/tasks/today", summary="获取今日学习任务")
async def get_today_tasks(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[DailyTaskResponse]]:
    """获取今天的学习任务"""
    # TODO: 实现真实的数据库查询
    demo_tasks = [
        {
            "id": 1,
            "plan_id": 1,
            "task_date": date.today(),
            "title": "学习React useCallback优化",
            "description": "深入理解useCallback的使用场景和性能优化原理",
            "task_type": "reading",
            "estimated_duration": 60,
            "actual_duration": None,
            "completed": False,
            "feedback": None,
            "created_at": datetime.now(),
            "completed_at": None,
        },
        {
            "id": 2,
            "plan_id": 1,
            "task_date": date.today(),
            "title": "练习React性能优化技巧",
            "description": "实现一个复杂组件的性能优化",
            "task_type": "practice",
            "estimated_duration": 90,
            "actual_duration": None,
            "completed": False,
            "feedback": None,
            "created_at": datetime.now(),
            "completed_at": None,
        },
    ]
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="获取今日任务成功",
        data=demo_tasks
    )


@router.get("/plans/{plan_id}/tasks", summary="获取计划的所有任务")
async def get_plan_tasks(
    plan_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> PaginatedResponse[DailyTaskResponse]:
    """获取指定学习计划的所有任务"""
    # TODO: 实现真实的数据库查询
    demo_tasks = [
        {
            "id": 1,
            "plan_id": plan_id,
            "task_date": date.today(),
            "title": "学习任务1",
            "description": "任务描述",
            "task_type": "reading",
            "estimated_duration": 60,
            "actual_duration": 55,
            "completed": True,
            "feedback": "学到很多",
            "created_at": datetime.now(),
            "completed_at": datetime.now(),
        },
    ]
    
    total = len(demo_tasks)
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        message="获取任务列表成功",
        data=demo_tasks,
        meta=PaginationMeta(
            page=skip // limit + 1,
            page_size=limit,
            total=total,
            total_pages=total_pages
        )
    )


@router.post("/tasks", summary="创建学习任务")
async def create_task(
    task: DailyTaskCreate,
    db: Session = Depends(get_db)
) -> BaseResponse[DailyTaskResponse]:
    """创建新的学习任务"""
    # TODO: 实现真实的数据库创建
    new_task = {
        "id": 3,
        "plan_id": task.plan_id,
        "task_date": task.task_date,
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "estimated_duration": task.estimated_duration,
        "actual_duration": None,
        "completed": False,
        "feedback": None,
        "created_at": datetime.now(),
        "completed_at": None,
    }
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习任务创建成功",
        data=new_task
    )


@router.put("/tasks/{task_id}", summary="更新学习任务")
async def update_task(
    task_id: int,
    task: DailyTaskUpdate,
    db: Session = Depends(get_db)
) -> BaseResponse[DailyTaskResponse]:
    """更新学习任务"""
    # TODO: 实现真实的数据库更新
    updated_task = {
        "id": task_id,
        "plan_id": 1,
        "task_date": date.today(),
        "title": task.title or "学习任务",
        "description": task.description,
        "task_type": "practice",
        "estimated_duration": 60,
        "actual_duration": task.actual_duration,
        "completed": task.completed if task.completed is not None else False,
        "feedback": task.feedback,
        "created_at": datetime.now(),
        "completed_at": datetime.now() if task.completed else None,
    }
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习任务更新成功",
        data=updated_task
    )


@router.delete("/tasks/{task_id}", summary="删除学习任务")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[None]:
    """删除学习任务"""
    # TODO: 实现真实的数据库删除
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="学习任务删除成功",
        data=None
    )
