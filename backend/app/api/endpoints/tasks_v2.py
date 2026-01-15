"""任务相关API端点 - 重构版"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import Task
from app.api.schemas import (
    BaseResponse,
    PaginatedResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from app.api.utils import (
    success_response,
    paginated_response,
    calculate_pagination,
    ResourceNotFoundError
)


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TaskResponse])
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Query("default_user", description="用户ID"),
    status: Optional[str] = Query(None, regex="^(pending|in_progress|completed|cancelled)$", description="任务状态"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$", description="优先级"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    db: Session = Depends(get_db)
):
    """
    获取任务列表（支持分页和筛选）
    
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    - **user_id**: 用户ID
    - **status**: 筛选任务状态 (pending/in_progress/completed/cancelled)
    - **priority**: 筛选优先级 (low/medium/high)
    - **tag**: 筛选标签
    """
    skip, limit = calculate_pagination(page, page_size)
    
    # 构建查询
    query = db.query(Task).filter(Task.user_id == user_id)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if tag:
        # 简单的标签筛选（假设tags字段是逗号分隔的字符串）
        query = query.filter(Task.tags.like(f"%{tag}%"))
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据（按创建时间倒序）
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    task_responses = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date,
            "tags": task.tags.split(",") if task.tags else [],
            "status": task.status,
            "progress": task.progress or 0,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        task_responses.append(TaskResponse(**task_dict))
    
    return paginated_response(
        data=task_responses,
        page=page,
        page_size=page_size,
        total=total,
        message="获取任务列表成功"
    )


@router.get("/{task_id}", response_model=BaseResponse[TaskResponse])
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ResourceNotFoundError("任务", task_id)
    
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "tags": task.tags.split(",") if task.tags else [],
        "status": task.status,
        "progress": task.progress or 0,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at
    }
    
    return success_response(
        data=TaskResponse(**task_dict),
        message="获取任务详情成功"
    )


@router.post("/", response_model=BaseResponse[TaskResponse])
async def create_task(
    task_data: TaskCreate,
    user_id: str = Query("default_user", description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    创建任务
    
    - 支持设置标题、描述、优先级、截止日期、标签等
    - 自动记录创建时间
    """
    # 创建任务对象
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=",".join(task_data.tags) if task_data.tags else None,
        status="pending",
        progress=0,
        created_at=datetime.now()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "tags": task.tags.split(",") if task.tags else [],
        "status": task.status,
        "progress": task.progress or 0,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at
    }
    
    return success_response(
        data=TaskResponse(**task_dict),
        message="创建任务成功"
    )


@router.put("/{task_id}", response_model=BaseResponse[TaskResponse])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ResourceNotFoundError("任务", task_id)
    
    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    
    # 处理tags
    if "tags" in update_data and update_data["tags"]:
        update_data["tags"] = ",".join(update_data["tags"])
    
    # 如果状态变为completed，记录完成时间
    if "status" in update_data and update_data["status"] == "completed":
        update_data["completed_at"] = datetime.now()
        update_data["progress"] = 100
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "tags": task.tags.split(",") if task.tags else [],
        "status": task.status,
        "progress": task.progress or 0,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at
    }
    
    return success_response(
        data=TaskResponse(**task_dict),
        message="更新任务成功"
    )


@router.delete("/{task_id}", response_model=BaseResponse[None])
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ResourceNotFoundError("任务", task_id)
    
    db.delete(task)
    db.commit()
    
    return success_response(
        data=None,
        message="删除任务成功"
    )


@router.patch("/{task_id}/complete", response_model=BaseResponse[TaskResponse])
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    """标记任务为已完成"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ResourceNotFoundError("任务", task_id)
    
    task.status = "completed"
    task.progress = 100
    task.completed_at = datetime.now()
    task.updated_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "tags": task.tags.split(",") if task.tags else [],
        "status": task.status,
        "progress": task.progress or 0,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at
    }
    
    return success_response(
        data=TaskResponse(**task_dict),
        message="标记任务完成成功"
    )


@router.patch("/{task_id}/progress", response_model=BaseResponse[TaskResponse])
async def update_task_progress(
    task_id: int,
    progress: int = Query(..., ge=0, le=100, description="进度（0-100）"),
    db: Session = Depends(get_db)
):
    """更新任务进度"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise ResourceNotFoundError("任务", task_id)
    
    task.progress = progress
    task.updated_at = datetime.now()
    
    # 如果进度达到100%，自动标记为完成
    if progress == 100:
        task.status = "completed"
        task.completed_at = datetime.now()
    elif task.status == "pending":
        task.status = "in_progress"
    
    db.commit()
    db.refresh(task)
    
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "tags": task.tags.split(",") if task.tags else [],
        "status": task.status,
        "progress": task.progress or 0,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at
    }
    
    return success_response(
        data=TaskResponse(**task_dict),
        message="更新任务进度成功"
    )
