"""数据库模型定义"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


# ========== 枚举类型 ==========

class MessageRole(str, enum.Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(str, enum.Enum):
    """意图类型"""
    CHAT = "chat"           # 闲聊
    QUERY = "query"         # 信息查询
    ACTION = "action"       # 执行任务
    STATUS = "status"       # 查询状态
    SYSTEM = "system"       # 系统控制


class MemoryType(str, enum.Enum):
    """记忆类型"""
    IDENTITY = "identity"       # 身份信息
    RELATIONSHIP = "relationship"  # 关系信息
    PREFERENCE = "preference"   # 偏好信息
    EPISODE = "episode"         # 情景记忆
    SEMANTIC = "semantic"       # 语义记忆
    PROCEDURAL = "procedural"   # 程序记忆（习惯）


# ========== 对话系统模型 ==========

class Session(Base):
    """对话会话模型"""
    __tablename__ = "sessions"
    
    id = Column(String(100), primary_key=True)  # UUID
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(200))  # 会话标题（自动生成）
    summary = Column(Text)  # 会话摘要
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """对话消息模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # 消息元数据
    intent = Column(String(50))  # chat, query, action, status
    intent_confidence = Column(Float)  # 意图置信度
    entities = Column(JSON)  # 提取的实体
    agent_used = Column(String(50))  # 调用的Agent
    task_id = Column(Integer)  # 关联的任务ID
    action_result = Column(JSON)  # 任务执行结果
    
    # 情感分析
    emotion = Column(String(50))  # 检测到的情绪
    emotion_score = Column(Float)  # 情绪分数
    
    # 响应质量
    response_time_ms = Column(Integer)  # 响应时间
    feedback = Column(String(20))  # positive, negative, null
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("Session", back_populates="messages")


# ========== 用户记忆系统模型 ==========

class UserProfile(Base):
    """用户档案模型 - 身份记忆"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # 基本信息
    name = Column(String(100))  # 姓名
    nickname = Column(String(50))  # 昵称/称呼
    gender = Column(String(20))
    birthday = Column(DateTime)
    timezone = Column(String(50), default="Asia/Shanghai")
    language = Column(String(20), default="zh-CN")
    
    # 职业信息
    occupation = Column(String(100))  # 职业
    company = Column(String(100))  # 公司
    position = Column(String(100))  # 职位
    industry = Column(String(100))  # 行业
    
    # 交互偏好
    communication_style = Column(String(50), default="balanced")  # formal, casual, balanced
    response_length = Column(String(20), default="medium")  # short, medium, detailed
    proactive_level = Column(String(20), default="moderate")  # passive, moderate, proactive
    emoji_usage = Column(String(20), default="moderate")  # none, moderate, frequent
    
    # 时间偏好
    work_start_hour = Column(Integer, default=9)
    work_end_hour = Column(Integer, default=18)
    is_early_bird = Column(Boolean, default=True)  # 早起型
    
    # 额外属性（JSON存储）
    extra_info = Column(JSON)
    interests = Column(JSON)  # 兴趣爱好列表
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    relationships = relationship("UserRelationship", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")


class UserRelationship(Base):
    """用户关系图谱模型"""
    __tablename__ = "user_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    
    # 关系人信息
    person_name = Column(String(100), nullable=False)  # 关系人姓名
    relationship_type = Column(String(50), nullable=False)  # 关系类型：上级/同事/朋友/家人等
    
    # 详细信息
    phone = Column(String(50))
    email = Column(String(100))
    company = Column(String(100))
    position = Column(String(100))
    
    # 关系属性
    importance = Column(Integer, default=3)  # 1-5，重要程度
    interaction_frequency = Column(String(20), default="occasional")  # rare, occasional, frequent
    last_mentioned = Column(DateTime)  # 最后提及时间
    mention_count = Column(Integer, default=0)  # 提及次数
    
    # 备注和记录
    notes = Column(Text)  # 关于这个人的备注
    interaction_history = Column(JSON)  # 互动历史摘要
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("UserProfile", back_populates="relationships")


class UserMemory(Base):
    """用户情景记忆模型 - 存储重要对话片段和事件"""
    __tablename__ = "user_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    
    # 记忆内容
    memory_type = Column(String(50), nullable=False)  # episode, semantic, procedural
    content = Column(Text, nullable=False)  # 记忆内容
    summary = Column(String(500))  # 简短摘要
    
    # 来源信息
    source_session_id = Column(String(100))  # 来源会话
    source_message_id = Column(Integer)  # 来源消息
    
    # 记忆属性
    importance = Column(Float, default=0.5)  # 重要性 0-1
    confidence = Column(Float, default=1.0)  # 可信度 0-1
    emotion_context = Column(String(50))  # 情感上下文
    
    # 相关标签
    tags = Column(JSON)  # 标签列表
    entities = Column(JSON)  # 相关实体
    
    # 记忆管理
    access_count = Column(Integer, default=0)  # 访问次数
    last_accessed = Column(DateTime)  # 最后访问
    expires_at = Column(DateTime)  # 过期时间（可选）
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("UserProfile", back_populates="memories")


class UserPreference(Base):
    """用户偏好模型 - 细粒度偏好设置"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    
    # 偏好键值
    category = Column(String(50), nullable=False)  # 偏好类别：interaction, content, notification, agent
    key = Column(String(100), nullable=False)  # 偏好键
    value = Column(JSON, nullable=False)  # 偏好值
    
    # 来源
    source = Column(String(50), default="explicit")  # explicit(显式设置), inferred(推断)
    confidence = Column(Float, default=1.0)  # 推断时的置信度
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("UserProfile", back_populates="preferences")


class BehaviorPattern(Base):
    """用户行为模式模型 - 学习到的习惯"""
    __tablename__ = "behavior_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # 模式描述
    pattern_type = Column(String(50), nullable=False)  # time_based, action_based, context_based
    pattern_name = Column(String(200), nullable=False)  # 模式名称/描述
    
    # 模式规则
    trigger_conditions = Column(JSON)  # 触发条件
    expected_action = Column(JSON)  # 预期行为
    
    # 统计信息
    occurrence_count = Column(Integer, default=1)  # 发生次数
    confidence = Column(Float, default=0.5)  # 置信度
    last_triggered = Column(DateTime)  # 最后触发
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 主动服务模型 ==========

class ProactiveTask(Base):
    """主动服务任务模型"""
    __tablename__ = "proactive_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # 任务类型
    task_type = Column(String(50), nullable=False)  # reminder, suggestion, alert, greeting
    trigger_type = Column(String(50), nullable=False)  # time, event, condition
    
    # 触发条件
    trigger_time = Column(DateTime)  # 时间触发
    trigger_condition = Column(JSON)  # 条件触发
    
    # 任务内容
    title = Column(String(200), nullable=False)
    content = Column(Text)
    action_data = Column(JSON)  # 相关操作数据
    
    # 状态
    status = Column(String(20), default="pending")  # pending, triggered, completed, cancelled
    priority = Column(Integer, default=3)  # 1-5
    
    # 重复设置
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(JSON)  # 重复规则
    
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========== 原有模型保留 ==========

class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)  # 用户原始输入
    task_type = Column(String(50), nullable=False)  # 任务类型：info_retrieval, schedule, notification等
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    assigned_agent = Column(String(50))  # 分配的Agent
    result = Column(JSON, nullable=True)  # 任务结果（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Schedule(Base):
    """日程模型"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    location = Column(String(200))
    is_completed = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Reminder(Base):
    """提醒模型"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    remind_at = Column(DateTime, nullable=False)
    repeat_type = Column(String(20), default="once")  # once, daily, weekly, monthly
    priority = Column(String(20), default="medium")  # low, medium, high
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TodoItem(Base):
    """待办事项模型"""
    __tablename__ = "todo_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # low, medium, high
    due_date = Column(DateTime)
    tags = Column(String(200))  # 逗号分隔的标签
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Note(Base):
    """笔记模型"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    tags = Column(String(200))  # 逗号分隔的标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Meeting(Base):
    """会议模型"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Integer, default=60)  # 分钟
    attendees = Column(Text)  # 逗号分隔的参会人
    location = Column(String(200))
    agenda = Column(Text)
    minutes = Column(Text)  # 会议纪要
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Contact(Base):
    """联系人模型"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50))
    email = Column(String(100))
    company = Column(String(100))
    position = Column(String(100))
    tags = Column(String(200))  # 逗号分隔的标签
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentLog(Base):
    """Agent执行日志"""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False)
    task_id = Column(Integer)
    action = Column(String(100))  # Agent执行的动作
    input_data = Column(JSON)  # 输入数据
    output_data = Column(JSON)  # 输出数据
    execution_time = Column(Integer)  # 执行时间（毫秒）
    status = Column(String(20))  # success, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== 知识图谱相关模型 ==========

class KnowledgeNode(Base):
    """知识图谱节点（实体）"""
    __tablename__ = "knowledge_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)  # 实体名称
    entity_type = Column(String(50), nullable=False)  # 实体类型：人物/组织/概念/事件等
    properties = Column(JSON)  # 实体属性（JSON格式）
    description = Column(Text)  # 实体描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    outgoing_relations = relationship("KnowledgeRelation", foreign_keys="KnowledgeRelation.source_id", back_populates="source")
    incoming_relations = relationship("KnowledgeRelation", foreign_keys="KnowledgeRelation.target_id", back_populates="target")


class KnowledgeRelation(Base):
    """知识图谱关系（边）"""
    __tablename__ = "knowledge_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)  # 源节点
    target_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)  # 目标节点
    relation_type = Column(String(50), nullable=False, index=True)  # 关系类型
    properties = Column(JSON)  # 关系属性
    weight = Column(Float, default=1.0)  # 关系权重
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    source = relationship("KnowledgeNode", foreign_keys=[source_id], back_populates="outgoing_relations")
    target = relationship("KnowledgeNode", foreign_keys=[target_id], back_populates="incoming_relations")


# ========== RAG相关模型 ==========

class DocumentChunk(Base):
    """文档片段（用于RAG）"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # 文档内容
    summary = Column(Text)  # 摘要
    keywords = Column(String(500))  # 关键词（逗号分隔）
    doc_metadata = Column(JSON)  # 元数据（标题、作者、分类等）- 使用doc_metadata避免与SQLAlchemy冲突
    chunk_index = Column(Integer, default=0)  # 片段序号
    parent_document_id = Column(Integer)  # 父文档ID（如果有）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    embeddings = relationship("VectorEmbedding", back_populates="chunk")


class VectorEmbedding(Base):
    """向量嵌入（用于语义检索）"""
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False)
    embedding_vector = Column(Text)  # 向量（序列化为字符串）
    embedding_model = Column(String(50), default="text-embedding-ada-002")  # 使用的嵌入模型
    dimension = Column(Integer, default=1536)  # 向量维度
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    chunk = relationship("DocumentChunk", back_populates="embeddings")


# ========== MCP相关模型 ==========

class MCPContext(Base):
    """MCP上下文（对话历史和状态）"""
    __tablename__ = "mcp_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)  # 会话ID
    user_id = Column(String(100))  # 用户ID
    context_data = Column(JSON)  # 上下文数据
    context_window = Column(JSON)  # 对话窗口
    state = Column(JSON)  # 会话状态
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MCPToolCall(Base):
    """MCP工具调用记录"""
    __tablename__ = "mcp_tool_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False)
    parameters = Column(JSON)
    result = Column(JSON)
    execution_time = Column(Integer)  # 执行时间（毫秒）
    status = Column(String(20))  # success, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

