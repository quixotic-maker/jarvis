"""
Agent管理API端点

提供：
- Agent列表和详情
- Agent状态监控
- Agent执行历史
- Agent性能统计
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.api.schemas import BaseResponse, PaginatedResponse

router = APIRouter()


# ==================== Pydantic Models ====================

class AgentInfo(BaseModel):
    """Agent信息"""
    id: str
    name: str
    description: str
    category: str
    category_label: str
    status: str  # idle, busy, error
    last_active: str
    capabilities: List[str]
    total_executions: int
    success_rate: float
    avg_response_time: float
    
    class Config:
        from_attributes = True


class AgentExecution(BaseModel):
    """Agent执行记录"""
    id: int
    agent_name: str
    task_type: str
    input_data: dict
    output_data: Optional[dict]
    status: str  # success, failed, running
    execution_time: float
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentStats(BaseModel):
    """Agent统计信息"""
    total_agents: int
    active_agents: int
    total_executions: int
    success_rate: float
    avg_response_time: float
    executions_by_category: dict
    executions_today: int


# ==================== Agent信息端点 ====================

@router.get("/list", summary="获取Agent列表")
async def get_agents_list(
    category: Optional[str] = Query(default=None, description="分类筛选"),
    status: Optional[str] = Query(default=None, pattern="^(idle|busy|error)$"),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[AgentInfo]]:
    """
    获取所有Agent列表
    
    支持按分类、状态筛选和关键词搜索
    """
    # TODO: 实现真实的数据库查询
    # 模拟21个Agent数据
    demo_agents = [
        # 办公效率类 (7个)
        {
            "id": "1",
            "name": "ScheduleAgent",
            "description": "智能日程管理，自动提取时间、地点、参与者，冲突检测",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "2分钟前",
            "capabilities": ["日程创建", "冲突检测", "智能提醒"],
            "total_executions": 156,
            "success_rate": 98.5,
            "avg_response_time": 0.3,
        },
        {
            "id": "2",
            "name": "TaskAgent",
            "description": "待办事项管理，优先级设置，进度跟踪",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "5分钟前",
            "capabilities": ["任务管理", "优先级", "进度跟踪"],
            "total_executions": 203,
            "success_rate": 99.0,
            "avg_response_time": 0.2,
        },
        {
            "id": "3",
            "name": "EmailAgent",
            "description": "智能邮件助手，自动撰写邮件，调整语气",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "10分钟前",
            "capabilities": ["邮件撰写", "语气调整", "模板生成"],
            "total_executions": 87,
            "success_rate": 95.2,
            "avg_response_time": 1.2,
        },
        {
            "id": "4",
            "name": "MeetingAgent",
            "description": "会议管理和协作，会议安排，纪要生成",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "15分钟前",
            "capabilities": ["会议安排", "纪要生成", "行动项跟进"],
            "total_executions": 64,
            "success_rate": 97.3,
            "avg_response_time": 0.5,
        },
        {
            "id": "5",
            "name": "FileAgent",
            "description": "文件管理和搜索，智能整理建议",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "20分钟前",
            "capabilities": ["文件搜索", "智能整理", "分类管理"],
            "total_executions": 142,
            "success_rate": 96.8,
            "avg_response_time": 0.4,
        },
        {
            "id": "6",
            "name": "NoteAgent",
            "description": "笔记管理和知识整理",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "25分钟前",
            "capabilities": ["笔记分类", "标签管理", "知识库"],
            "total_executions": 119,
            "success_rate": 98.1,
            "avg_response_time": 0.3,
        },
        {
            "id": "7",
            "name": "ReminderAgent",
            "description": "智能提醒管理，定时提醒，重复提醒",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "30分钟前",
            "capabilities": ["定时提醒", "重复提醒", "优先级设置"],
            "total_executions": 245,
            "success_rate": 99.5,
            "avg_response_time": 0.1,
        },
        
        # 技术开发类 (3个)
        {
            "id": "8",
            "name": "CodeAgent",
            "description": "代码生成和辅助开发",
            "category": "tech",
            "category_label": "技术开发",
            "status": "idle",
            "last_active": "1小时前",
            "capabilities": ["代码生成", "代码解释", "Bug修复"],
            "total_executions": 78,
            "success_rate": 92.3,
            "avg_response_time": 2.1,
        },
        {
            "id": "9",
            "name": "DataAnalysisAgent",
            "description": "数据分析和洞察",
            "category": "tech",
            "category_label": "技术开发",
            "status": "idle",
            "last_active": "2小时前",
            "capabilities": ["数据统计", "趋势分析", "可视化建议"],
            "total_executions": 45,
            "success_rate": 94.7,
            "avg_response_time": 1.8,
        },
        {
            "id": "10",
            "name": "CalculationAgent",
            "description": "数学计算和数据处理",
            "category": "tech",
            "category_label": "技术开发",
            "status": "idle",
            "last_active": "3小时前",
            "capabilities": ["数学运算", "单位转换", "统计分析"],
            "total_executions": 167,
            "success_rate": 99.8,
            "avg_response_time": 0.05,
        },
        
        # 学习成长类 (2个)
        {
            "id": "11",
            "name": "LearningAgent",
            "description": "学习辅助和知识管理",
            "category": "learning",
            "category_label": "学习成长",
            "status": "idle",
            "last_active": "1天前",
            "capabilities": ["学习计划", "概念解释", "测验生成"],
            "total_executions": 34,
            "success_rate": 96.2,
            "avg_response_time": 1.5,
        },
        {
            "id": "12",
            "name": "InfoRetrievalAgent",
            "description": "信息检索和问答",
            "category": "learning",
            "category_label": "学习成长",
            "status": "idle",
            "last_active": "2小时前",
            "capabilities": ["知识问答", "概念解释", "信息搜索"],
            "total_executions": 189,
            "success_rate": 97.8,
            "avg_response_time": 0.6,
        },
        
        # 生活服务类 (9个)
        {
            "id": "13",
            "name": "WeatherAgent",
            "description": "天气查询和预报",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "30分钟前",
            "capabilities": ["天气查询", "未来预报", "穿衣建议"],
            "total_executions": 234,
            "success_rate": 98.9,
            "avg_response_time": 0.4,
        },
        {
            "id": "14",
            "name": "NewsAgent",
            "description": "新闻获取和摘要",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "1小时前",
            "capabilities": ["新闻获取", "摘要生成", "个性化推荐"],
            "total_executions": 156,
            "success_rate": 96.5,
            "avg_response_time": 0.8,
        },
        {
            "id": "15",
            "name": "TravelAgent",
            "description": "旅行规划和建议",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "2天前",
            "capabilities": ["行程规划", "景点推荐", "预算建议"],
            "total_executions": 23,
            "success_rate": 94.1,
            "avg_response_time": 2.3,
        },
        {
            "id": "16",
            "name": "HealthAgent",
            "description": "健康管理和建议",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "1天前",
            "capabilities": ["健康建议", "运动计划", "饮食计划"],
            "total_executions": 67,
            "success_rate": 95.8,
            "avg_response_time": 1.1,
        },
        {
            "id": "17",
            "name": "RecommendationAgent",
            "description": "个性化推荐",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "3小时前",
            "capabilities": ["电影推荐", "书籍推荐", "音乐推荐"],
            "total_executions": 98,
            "success_rate": 93.7,
            "avg_response_time": 0.9,
        },
        {
            "id": "18",
            "name": "TranslationAgent",
            "description": "多语言翻译",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "1小时前",
            "capabilities": ["多语言互译", "自动检测", "地道翻译"],
            "total_executions": 312,
            "success_rate": 97.2,
            "avg_response_time": 0.5,
        },
        {
            "id": "19",
            "name": "SummaryAgent",
            "description": "文本摘要和要点提取",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "2小时前",
            "capabilities": ["文本总结", "关键信息提取", "要点列表"],
            "total_executions": 145,
            "success_rate": 96.3,
            "avg_response_time": 0.7,
        },
        {
            "id": "20",
            "name": "ContactAgent",
            "description": "联系人管理",
            "category": "life",
            "category_label": "生活服务",
            "status": "idle",
            "last_active": "5小时前",
            "capabilities": ["联系人管理", "关系管理", "沟通记录"],
            "total_executions": 56,
            "success_rate": 98.2,
            "avg_response_time": 0.2,
        },
        {
            "id": "21",
            "name": "Coordinator",
            "description": "主控Agent，智能调度",
            "category": "life",
            "category_label": "生活服务",
            "status": "busy",
            "last_active": "刚刚",
            "capabilities": ["任务分析", "Agent调度", "结果整合"],
            "total_executions": 567,
            "success_rate": 99.1,
            "avg_response_time": 0.4,
        },
    ]
    
    # 按分类筛选
    if category and category != "all":
        demo_agents = [a for a in demo_agents if a["category"] == category]
    
    # 按状态筛选
    if status:
        demo_agents = [a for a in demo_agents if a["status"] == status]
    
    # 搜索
    if search:
        search_lower = search.lower()
        demo_agents = [
            a for a in demo_agents
            if search_lower in a["name"].lower() or 
               search_lower in a["description"].lower()
        ]
    
    return BaseResponse(
        success=True,
        data=demo_agents
    )


@router.get("/{agent_id}", summary="获取Agent详情")
async def get_agent_detail(
    agent_id: str,
    db: Session = Depends(get_db)
) -> BaseResponse[AgentInfo]:
    """获取指定Agent的详细信息"""
    # TODO: 实现真实的数据库查询
    if agent_id == "1":
        agent = {
            "id": "1",
            "name": "ScheduleAgent",
            "description": "智能日程管理，自动提取时间、地点、参与者，冲突检测",
            "category": "office",
            "category_label": "办公效率",
            "status": "idle",
            "last_active": "2分钟前",
            "capabilities": ["日程创建", "冲突检测", "智能提醒"],
            "total_executions": 156,
            "success_rate": 98.5,
            "avg_response_time": 0.3,
        }
        return BaseResponse(success=True, data=agent)
    
    raise HTTPException(status_code=404, detail="Agent不存在")


@router.get("/{agent_name}/executions", summary="获取Agent执行历史")
async def get_agent_executions(
    agent_name: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> PaginatedResponse[AgentExecution]:
    """获取指定Agent的执行历史记录"""
    # TODO: 实现真实的数据库查询
    demo_executions = [
        {
            "id": 1,
            "agent_name": agent_name,
            "task_type": "create_schedule",
            "input_data": {"message": "明天下午3点开会"},
            "output_data": {"schedule_id": 123, "title": "会议"},
            "status": "success",
            "execution_time": 0.25,
            "error_message": None,
            "created_at": datetime.now() - timedelta(minutes=5),
            "completed_at": datetime.now() - timedelta(minutes=5),
        },
        {
            "id": 2,
            "agent_name": agent_name,
            "task_type": "check_conflicts",
            "input_data": {"schedule_id": 123},
            "output_data": {"conflicts": []},
            "status": "success",
            "execution_time": 0.15,
            "error_message": None,
            "created_at": datetime.now() - timedelta(hours=1),
            "completed_at": datetime.now() - timedelta(hours=1),
        },
    ]
    
    return PaginatedResponse(
        success=True,
        data=demo_executions,
        total=len(demo_executions),
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/stats/overview", summary="获取Agent统计概览")
async def get_agents_stats(
    db: Session = Depends(get_db)
) -> BaseResponse[AgentStats]:
    """获取所有Agent的统计信息"""
    # TODO: 实现真实的数据库查询
    stats = {
        "total_agents": 21,
        "active_agents": 20,
        "total_executions": 3156,
        "success_rate": 97.3,
        "avg_response_time": 0.6,
        "executions_by_category": {
            "office": 1016,
            "tech": 290,
            "learning": 223,
            "life": 1627,
        },
        "executions_today": 187,
    }
    
    return BaseResponse(
        success=True,
        data=stats
    )
