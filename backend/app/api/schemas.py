"""
API通用Schema定义
统一的请求和响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Generic, TypeVar
from datetime import datetime
from enum import Enum

# ==================== 通用响应模型 ====================

T = TypeVar('T')


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    status: ResponseStatus = Field(..., description="响应状态")
    message: str = Field("", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "操作成功",
                "data": None,
                "timestamp": "2026-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应"""
    status: ResponseStatus = ResponseStatus.ERROR
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(1, ge=1, description="当前页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    total: int = Field(0, ge=0, description="总记录数")
    total_pages: int = Field(0, ge=0, description="总页数")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = ""
    data: List[T] = Field(default_factory=list)
    meta: PaginationMeta
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== 用户相关Schema ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 日程相关Schema ====================

class ScheduleBase(BaseModel):
    """日程基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    event_type: str = Field("event", pattern="^(meeting|task|reminder|event)$")


class ScheduleCreate(ScheduleBase):
    """创建日程"""
    pass


class ScheduleUpdate(BaseModel):
    """更新日程"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    event_type: Optional[str] = Field(None, pattern="^(meeting|task|reminder|event)$")
    is_completed: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    """日程响应"""
    id: int
    user_id: str
    is_completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def model_validate(cls, obj):
        """自定义验证：转换attendees字符串为列表"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
            # 转换attendees字符串为列表
            if 'attendees' in data and isinstance(data['attendees'], str):
                data['attendees'] = [a.strip() for a in data['attendees'].split(',')] if data['attendees'] else None
            return super().model_validate(data)
        return super().model_validate(obj)
    
    class Config:
        from_attributes = True


# ==================== 任务相关Schema ====================

class TaskBase(BaseModel):
    """任务基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskCreate(TaskBase):
    """创建任务"""
    pass


class TaskUpdate(BaseModel):
    """更新任务"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")


class TaskResponse(TaskBase):
    """任务响应"""
    id: int
    user_id: str
    status: str = "pending"
    progress: int = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @classmethod
    def model_validate(cls, obj):
        """自定义验证：转换tags字符串为列表"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
            # 转换tags字符串为列表
            if 'tags' in data and isinstance(data['tags'], str):
                data['tags'] = [t.strip() for t in data['tags'].split(',')] if data['tags'] else None
            return super().model_validate(data)
        return super().model_validate(obj)
    
    class Config:
        from_attributes = True


# ==================== 笔记相关Schema ====================

class NoteBase(BaseModel):
    """笔记基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class NoteCreate(NoteBase):
    """创建笔记"""
    pass


class NoteUpdate(BaseModel):
    """更新笔记"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class NoteResponse(NoteBase):
    """笔记响应"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== 学习相关Schema ====================

class LearningPlanBase(BaseModel):
    """学习计划基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target: str
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class LearningPlanCreate(LearningPlanBase):
    """创建学习计划"""
    pass


class LearningPlanUpdate(BaseModel):
    """更新学习计划"""
    title: Optional[str] = None
    description: Optional[str] = None
    target: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, pattern="^(active|paused|completed|cancelled)$")


class LearningPlanResponse(LearningPlanBase):
    """学习计划响应"""
    id: int
    user_id: str
    progress: int = 0
    status: str = "active"
    tasks_total: int = 0
    tasks_completed: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LearningResourceBase(BaseModel):
    """学习资源基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    resource_type: str = Field(..., pattern="^(video|article|book|course|doc)$")
    url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class LearningResourceCreate(LearningResourceBase):
    """创建学习资源"""
    pass


class LearningResourceUpdate(BaseModel):
    """更新学习资源"""
    title: Optional[str] = None
    resource_type: Optional[str] = Field(None, pattern="^(video|article|book|course|doc)$")
    url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class LearningResourceResponse(LearningResourceBase):
    """学习资源响应"""
    id: int
    user_id: str
    progress: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== 知识图谱相关Schema ====================

class KnowledgeNodeBase(BaseModel):
    """知识节点基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    node_type: str = Field(..., pattern="^(concept|skill|project|resource|person)$")
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeNodeCreate(KnowledgeNodeBase):
    """创建知识节点"""
    pass


class KnowledgeNodeUpdate(BaseModel):
    """更新知识节点"""
    title: Optional[str] = None
    node_type: Optional[str] = Field(None, pattern="^(concept|skill|project|resource|person)$")
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeNodeResponse(KnowledgeNodeBase):
    """知识节点响应"""
    id: int
    user_id: str
    connections: int = 0  # 连接数
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KnowledgeEdgeCreate(BaseModel):
    """创建知识连接"""
    source_id: int
    target_id: int
    relation_type: str = Field("related", max_length=50)
    description: Optional[str] = None


# ==================== 设置相关Schema ====================

class SystemPreferences(BaseModel):
    """系统偏好设置"""
    theme: str = Field("dark", pattern="^(light|dark|auto)$")
    language: str = Field("zh-CN", pattern="^(zh-CN|en-US|ja-JP)$")
    font_size: str = Field("medium", pattern="^(small|medium|large)$")
    sound_enabled: bool = True
    notifications_enabled: bool = True
    auto_save: bool = True


class AgentPreferences(BaseModel):
    """Agent偏好设置"""
    default_agent: str = "coordinator"
    response_speed: str = Field("balanced", pattern="^(fast|balanced|quality)$")
    creativity: int = Field(70, ge=0, le=100)
    max_tokens: int = Field(2000, ge=100, le=4000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    enable_voice: bool = True
    enable_memory: bool = True


class UserSettings(BaseModel):
    """用户设置"""
    system: SystemPreferences
    agent: AgentPreferences


class SettingsResponse(BaseModel):
    """设置响应"""
    user_id: str
    settings: UserSettings
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 对话相关Schema ====================

class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    user_id: str = "default_user"
    stream: bool = False  # 是否流式响应


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str
    message_id: int
    content: str
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    agent_used: Optional[str] = None
    action_result: Optional[Any] = None
    suggestions: Optional[List[str]] = None
    response_time_ms: int


# ==================== Agent相关Schema ====================

class AgentInfo(BaseModel):
    """Agent信息"""
    name: str
    display_name: str
    description: str
    category: str
    capabilities: List[str]
    status: str = "active"


class AgentStats(BaseModel):
    """Agent统计"""
    total_calls: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: int = 0
    last_used: Optional[datetime] = None


class AgentDetailResponse(BaseModel):
    """Agent详情响应"""
    info: AgentInfo
    stats: AgentStats


# ==================== 统计相关Schema ====================

class DashboardStats(BaseModel):
    """仪表盘统计"""
    total_conversations: int = 0
    total_tasks: int = 0
    total_schedules: int = 0
    total_notes: int = 0
    active_learning_plans: int = 0
    knowledge_nodes: int = 0
    agent_calls_today: int = 0
    avg_response_time_ms: int = 0
