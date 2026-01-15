"""提醒相关API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import Reminder
from pydantic import BaseModel


router = APIRouter()


class ReminderResponse(BaseModel):
    """提醒响应模型"""
    id: int
    title: str
    message: str | None
    remind_at: datetime
    repeat_type: str
    priority: str
    is_triggered: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[ReminderResponse])
async def get_reminders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取提醒列表"""
    reminders = db.query(Reminder).order_by(Reminder.remind_at).offset(skip).limit(limit).all()
    return reminders


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """删除提醒"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "提醒已删除", "reminder_id": reminder_id}
