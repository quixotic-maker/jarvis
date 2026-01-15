"""日程相关API端点"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import Schedule
from app.api.schemas import (
    BaseResponse,
    PaginatedResponse,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse
)
from app.api.utils import (
    success_response,
    paginated_response,
    calculate_pagination,
    ResourceNotFoundError
)


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ScheduleResponse])
async def get_schedules(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Query("default_user", description="用户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    is_completed: Optional[bool] = Query(None, description="是否已完成"),
    db: Session = Depends(get_db)
):
    """
    获取日程列表（支持分页和筛选）
    
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    - **user_id**: 用户ID
    - **start_date**: 筛选开始日期
    - **end_date**: 筛选结束日期
    - **is_completed**: 筛选是否完成
    """
    skip, limit = calculate_pagination(page, page_size)
    
    # 构建查询
    query = db.query(Schedule).filter(Schedule.user_id == user_id)
    
    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.start_time <= end_date)
    if is_completed is not None:
        query = query.filter(Schedule.is_completed == is_completed)
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    schedules = query.order_by(Schedule.start_time.desc()).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    schedule_responses = [ScheduleResponse.model_validate(s) for s in schedules]
    
    return paginated_response(
        data=schedule_responses,
        page=page,
        page_size=page_size,
        total=total,
        message="获取日程列表成功"
    )


@router.get("/{schedule_id}", response_model=BaseResponse[ScheduleResponse])
async def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """获取单个日程详情"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ResourceNotFoundError("日程", schedule_id)
    
    return success_response(
        data=ScheduleResponse.model_validate(schedule),
        message="获取日程详情成功"
    )


@router.post("/", response_model=BaseResponse[ScheduleResponse])
async def create_schedule(
    schedule_data: ScheduleCreate,
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    创建日程
    
    - 支持设置标题、描述、时间、地点等
    - 自动记录创建时间
    """
    # 创建日程对象
    schedule = Schedule(
        user_id=user_id,
        title=schedule_data.title,
        description=schedule_data.description,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        location=schedule_data.location,
        attendees=",".join(schedule_data.attendees) if schedule_data.attendees else None,
        priority=schedule_data.priority,
        event_type=schedule_data.event_type,
        is_completed=False,
        created_at=datetime.now()
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    return success_response(
        data=ScheduleResponse.model_validate(schedule),
        message="创建日程成功"
    )


@router.put("/{schedule_id}", response_model=BaseResponse[ScheduleResponse])
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """更新日程"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ResourceNotFoundError("日程", schedule_id)
    
    # 更新字段
    update_data = schedule_data.model_dump(exclude_unset=True)
    
    # 处理attendees
    if "attendees" in update_data and update_data["attendees"]:
        update_data["attendees"] = ",".join(update_data["attendees"])
    
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.now()
    
    db.commit()
    db.refresh(schedule)
    
    return success_response(
        data=ScheduleResponse.model_validate(schedule),
        message="更新日程成功"
    )


@router.delete("/{schedule_id}", response_model=BaseResponse[None])
async def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """删除日程"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ResourceNotFoundError("日程", schedule_id)
    
    db.delete(schedule)
    db.commit()
    
    return success_response(
        data=None,
        message="删除日程成功"
    )


@router.patch("/{schedule_id}/complete", response_model=BaseResponse[ScheduleResponse])
async def complete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """标记日程为已完成"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ResourceNotFoundError("日程", schedule_id)
    
    schedule.is_completed = True
    schedule.updated_at = datetime.now()
    
    db.commit()
    db.refresh(schedule)
    
    return success_response(
        data=ScheduleResponse.model_validate(schedule),
        message="标记日程完成成功"
    )


@router.patch("/{schedule_id}/uncomplete", response_model=BaseResponse[ScheduleResponse])
async def uncomplete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """取消日程完成状态"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ResourceNotFoundError("日程", schedule_id)
    
    schedule.is_completed = False
    schedule.updated_at = datetime.now()
    
    db.commit()
    db.refresh(schedule)
    
    return success_response(
        data=ScheduleResponse.model_validate(schedule),
        message="取消日程完成成功"
    )

    
    schedule.is_completed = True
    db.commit()
    
    return {"message": "日程已标记为完成", "schedule_id": schedule_id}
