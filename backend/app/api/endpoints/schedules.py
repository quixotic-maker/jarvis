"""日程相关API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import Schedule
from pydantic import BaseModel


router = APIRouter()


class ScheduleResponse(BaseModel):
    """日程响应模型"""
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    location: str | None
    is_completed: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取日程列表"""
    schedules = db.query(Schedule).order_by(Schedule.start_time.desc()).offset(skip).limit(limit).all()
    return schedules


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """获取单个日程详情"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    return schedule


@router.patch("/{schedule_id}/complete")
async def complete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """标记日程为已完成"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    schedule.is_completed = True
    db.commit()
    
    return {"message": "日程已标记为完成", "schedule_id": schedule_id}
