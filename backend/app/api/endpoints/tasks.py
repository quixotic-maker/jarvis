"""任务相关API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import time

from app.db.database import get_db
from app.db.models import Task
from app.agents import get_agent, CoordinatorAgent
from pydantic import BaseModel


router = APIRouter()


class TaskCreate(BaseModel):
    """创建任务的请求模型"""
    user_input: str


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    user_input: str
    task_type: str
    status: str
    assigned_agent: str | None
    result: dict | None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    创建新任务
    用户输入自然语言，系统自动分析并执行
    """
    start_time = time.time()
    
    # 1. 使用主控Agent分析任务
    coordinator = CoordinatorAgent()
    analysis = await coordinator.execute({"user_input": task.user_input})
    
    if not analysis.get("success"):
        raise HTTPException(status_code=400, detail="任务分析失败")
    
    # 2. 创建任务记录
    db_task = Task(
        user_input=task.user_input,
        task_type=analysis["task_type"],
        assigned_agent=analysis["assigned_agent"],
        status="processing"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 3. 执行具体任务
    try:
        agent = get_agent(analysis["assigned_agent"])
        if not agent:
            result = {
                "success": False,
                "error": "未找到对应的Agent"
            }
        else:
            # 准备Agent输入
            agent_input = {
                "user_input": task.user_input,
                "parameters": analysis.get("parameters", {}),
                "db": db
            }
            
            # 根据不同Agent设置action
            if analysis["assigned_agent"] == "ScheduleAgent":
                agent_input["action"] = "create"  # 默认为创建
            elif analysis["assigned_agent"] == "ReminderAgent":
                agent_input["action"] = "create"
            elif analysis["assigned_agent"] == "EmailAgent":
                agent_input["action"] = "compose"
            elif analysis["assigned_agent"] == "FileAgent":
                agent_input["action"] = "search"
            elif analysis["assigned_agent"] == "TaskAgent":
                agent_input["action"] = "create"
            elif analysis["assigned_agent"] == "NoteAgent":
                agent_input["action"] = "create"
            elif analysis["assigned_agent"] == "MeetingAgent":
                agent_input["action"] = "schedule"
            elif analysis["assigned_agent"] == "ContactAgent":
                agent_input["action"] = "add"
            
            result = await agent.execute(agent_input)
        
        # 4. 更新任务状态
        db_task.status = "completed" if result.get("success") else "failed"
        db_task.result = result
        db.commit()
        db.refresh(db_task)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # 5. 记录日志
        if agent:
            agent.log_execution(
                db=db,
                task_id=db_task.id,
                action="execute_task",
                input_data=agent_input,
                output_data=result,
                execution_time=execution_time,
                status="success" if result.get("success") else "failed"
            )
        
        return db_task
        
    except Exception as e:
        db_task.status = "failed"
        db_task.result = {"error": str(e)}
        db.commit()
        raise HTTPException(status_code=500, detail=f"任务执行失败: {str(e)}")


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取任务列表"""
    tasks = db.query(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
