"""
记忆管理系统 - Jarvis的大脑

负责管理用户的长期记忆，包括：
- 身份记忆：用户基本信息
- 关系记忆：用户的社交关系
- 偏好记忆：用户的习惯偏好
- 情景记忆：重要对话片段
- 行为模式：学习到的用户习惯
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.db.models import (
    UserProfile, UserRelationship, UserMemory, 
    UserPreference, BehaviorPattern, Message
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """记忆管理器 - Jarvis的大脑"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_enabled = bool(settings.DEEPSEEK_API_KEY)
    
    # ==================== 用户档案管理 ====================
    
    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """获取或创建用户档案"""
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            logger.info(f"Created new user profile for {user_id}")
        
        return profile
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """更新用户档案"""
        profile = await self.get_or_create_profile(user_id)
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self.db.commit()
        self.db.refresh(profile)
        logger.info(f"Updated profile for {user_id}: {list(updates.keys())}")
        return profile
    
    async def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户档案摘要（用于上下文）"""
        profile = await self.get_or_create_profile(user_id)
        
        return {
            "name": profile.name or "用户",
            "nickname": profile.nickname,
            "occupation": profile.occupation,
            "company": profile.company,
            "communication_style": profile.communication_style,
            "response_length": profile.response_length,
            "interests": profile.interests or [],
            "timezone": profile.timezone,
            "is_early_bird": profile.is_early_bird,
            "work_hours": f"{profile.work_start_hour}:00-{profile.work_end_hour}:00"
        }
    
    # ==================== 关系图谱管理 ====================
    
    async def add_relationship(
        self, 
        user_id: str, 
        person_name: str, 
        relationship_type: str,
        **kwargs
    ) -> UserRelationship:
        """添加或更新关系"""
        # 检查是否已存在
        existing = self.db.query(UserRelationship).filter(
            and_(
                UserRelationship.user_id == user_id,
                UserRelationship.person_name == person_name
            )
        ).first()
        
        if existing:
            # 更新已有关系
            existing.relationship_type = relationship_type
            existing.mention_count += 1
            existing.last_mentioned = datetime.utcnow()
            for key, value in kwargs.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            relationship = existing
        else:
            # 创建新关系
            # 确保用户档案存在
            await self.get_or_create_profile(user_id)
            relationship = UserRelationship(
                user_id=user_id,
                person_name=person_name,
                relationship_type=relationship_type,
                last_mentioned=datetime.utcnow(),
                mention_count=1,
                **kwargs
            )
            self.db.add(relationship)
        
        self.db.commit()
        self.db.refresh(relationship)
        logger.info(f"Added/updated relationship: {person_name} ({relationship_type}) for {user_id}")
        return relationship
    
    async def get_relationships(
        self, 
        user_id: str, 
        relationship_type: Optional[str] = None
    ) -> List[UserRelationship]:
        """获取用户的关系列表"""
        query = self.db.query(UserRelationship).filter(
            UserRelationship.user_id == user_id
        )
        
        if relationship_type:
            query = query.filter(UserRelationship.relationship_type == relationship_type)
        
        return query.order_by(desc(UserRelationship.importance)).all()
    
    async def find_person(self, user_id: str, name: str) -> Optional[UserRelationship]:
        """根据名字查找关系人"""
        return self.db.query(UserRelationship).filter(
            and_(
                UserRelationship.user_id == user_id,
                UserRelationship.person_name.ilike(f"%{name}%")
            )
        ).first()
    
    async def get_relationship_context(self, user_id: str) -> str:
        """获取关系上下文（用于对话）"""
        relationships = await self.get_relationships(user_id)
        if not relationships:
            return ""
        
        context_lines = ["用户的关系网络:"]
        for rel in relationships[:10]:  # 只取前10个重要关系
            line = f"- {rel.person_name}: {rel.relationship_type}"
            if rel.company:
                line += f" ({rel.company})"
            context_lines.append(line)
        
        return "\n".join(context_lines)
    
    # ==================== 情景记忆管理 ====================
    
    async def store_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "episode",
        importance: float = 0.5,
        source_session_id: Optional[str] = None,
        source_message_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        entities: Optional[Dict] = None
    ) -> UserMemory:
        """存储新记忆"""
        # 确保用户档案存在
        await self.get_or_create_profile(user_id)
        
        # 生成摘要
        summary = content[:200] if len(content) > 200 else content
        
        memory = UserMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            summary=summary,
            importance=importance,
            source_session_id=source_session_id,
            source_message_id=source_message_id,
            tags=tags or [],
            entities=entities or {}
        )
        
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        logger.info(f"Stored memory for {user_id}: {summary[:50]}...")
        return memory
    
    async def search_memories(
        self,
        user_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[UserMemory]:
        """搜索记忆"""
        db_query = self.db.query(UserMemory).filter(
            and_(
                UserMemory.user_id == user_id,
                UserMemory.is_active == True
            )
        )
        
        if memory_type:
            db_query = db_query.filter(UserMemory.memory_type == memory_type)
        
        if query:
            db_query = db_query.filter(
                or_(
                    UserMemory.content.ilike(f"%{query}%"),
                    UserMemory.summary.ilike(f"%{query}%")
                )
            )
        
        memories = db_query.order_by(
            desc(UserMemory.importance),
            desc(UserMemory.created_at)
        ).limit(limit).all()
        
        # 更新访问次数
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()
        self.db.commit()
        
        return memories
    
    async def get_recent_memories(
        self, 
        user_id: str, 
        days: int = 7,
        limit: int = 20
    ) -> List[UserMemory]:
        """获取最近的记忆"""
        since = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(UserMemory).filter(
            and_(
                UserMemory.user_id == user_id,
                UserMemory.is_active == True,
                UserMemory.created_at >= since
            )
        ).order_by(desc(UserMemory.importance)).limit(limit).all()
    
    async def get_memory_context(self, user_id: str, current_query: str = "") -> str:
        """获取记忆上下文（用于对话）"""
        # 获取重要记忆
        important_memories = await self.search_memories(
            user_id, 
            query=current_query if current_query else None,
            limit=5
        )
        
        if not important_memories:
            return ""
        
        context_lines = ["相关记忆:"]
        for mem in important_memories:
            context_lines.append(f"- [{mem.memory_type}] {mem.summary}")
        
        return "\n".join(context_lines)
    
    # ==================== 偏好管理 ====================
    
    async def set_preference(
        self,
        user_id: str,
        category: str,
        key: str,
        value: Any,
        source: str = "explicit"
    ) -> UserPreference:
        """设置用户偏好"""
        # 确保用户档案存在
        await self.get_or_create_profile(user_id)
        
        # 检查是否已存在
        existing = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key
            )
        ).first()
        
        if existing:
            existing.value = value
            existing.source = source
            existing.updated_at = datetime.utcnow()
            pref = existing
        else:
            pref = UserPreference(
                user_id=user_id,
                category=category,
                key=key,
                value=value,
                source=source
            )
            self.db.add(pref)
        
        self.db.commit()
        self.db.refresh(pref)
        return pref
    
    async def get_preference(
        self,
        user_id: str,
        category: str,
        key: str,
        default: Any = None
    ) -> Any:
        """获取用户偏好"""
        pref = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key
            )
        ).first()
        
        return pref.value if pref else default
    
    async def get_all_preferences(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """获取所有偏好"""
        prefs = self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()
        
        result = {}
        for pref in prefs:
            if pref.category not in result:
                result[pref.category] = {}
            result[pref.category][pref.key] = pref.value
        
        return result
    
    # ==================== 行为模式学习 ====================
    
    async def record_behavior(
        self,
        user_id: str,
        pattern_type: str,
        pattern_name: str,
        trigger_conditions: Dict,
        expected_action: Dict
    ) -> BehaviorPattern:
        """记录行为模式"""
        # 查找相似模式
        existing = self.db.query(BehaviorPattern).filter(
            and_(
                BehaviorPattern.user_id == user_id,
                BehaviorPattern.pattern_name == pattern_name
            )
        ).first()
        
        if existing:
            existing.occurrence_count += 1
            existing.confidence = min(1.0, existing.confidence + 0.1)
            existing.last_triggered = datetime.utcnow()
            pattern = existing
        else:
            pattern = BehaviorPattern(
                user_id=user_id,
                pattern_type=pattern_type,
                pattern_name=pattern_name,
                trigger_conditions=trigger_conditions,
                expected_action=expected_action,
                last_triggered=datetime.utcnow()
            )
            self.db.add(pattern)
        
        self.db.commit()
        self.db.refresh(pattern)
        return pattern
    
    async def get_active_patterns(
        self, 
        user_id: str,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[BehaviorPattern]:
        """获取活跃的行为模式"""
        query = self.db.query(BehaviorPattern).filter(
            and_(
                BehaviorPattern.user_id == user_id,
                BehaviorPattern.is_active == True,
                BehaviorPattern.confidence >= min_confidence
            )
        )
        
        if pattern_type:
            query = query.filter(BehaviorPattern.pattern_type == pattern_type)
        
        return query.order_by(desc(BehaviorPattern.confidence)).all()
    
    # ==================== 信息提取 ====================
    
    async def extract_and_store_information(
        self,
        user_id: str,
        message: str,
        response: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """从对话中提取并存储信息"""
        
        if not self.llm_enabled:
            return {"extracted": False, "reason": "LLM not configured"}
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            
            extraction_prompt = """分析以下对话，提取以下信息（如果有的话）。只返回JSON，不要其他内容。

对话：
用户: {message}
助手: {response}

请提取：
1. identity_info: 用户透露的个人信息（姓名、职业、公司等）
2. relationships: 提到的人物及其关系（格式：[{{"name": "xxx", "relationship": "同事/上级/朋友/家人等", "detail": "其他信息"}}]）
3. preferences: 表达的喜好或习惯
4. important_events: 值得记住的事件（出差、会议、重要日期等）
5. emotion: 用户当前情绪（如果明显）

返回JSON格式，没有检测到的字段不要返回空值，直接不返回该字段。
""".format(message=message, response=response)

            llm_response = client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个信息提取专家，只返回JSON格式的结果。"},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = llm_response.choices[0].message.content.strip()
            
            # 清理JSON
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            extracted = json.loads(result_text)
            
            # 存储提取的信息
            stored = {"extracted": True, "stored": []}
            
            # 存储身份信息
            if "identity_info" in extracted and extracted["identity_info"]:
                await self.update_profile(user_id, extracted["identity_info"])
                stored["stored"].append("identity")
            
            # 存储关系
            if "relationships" in extracted and extracted["relationships"]:
                for rel in extracted["relationships"]:
                    if "name" in rel and "relationship" in rel:
                        await self.add_relationship(
                            user_id,
                            rel["name"],
                            rel["relationship"],
                            notes=rel.get("detail")
                        )
                stored["stored"].append("relationships")
            
            # 存储重要事件为情景记忆
            if "important_events" in extracted and extracted["important_events"]:
                for event in extracted["important_events"] if isinstance(extracted["important_events"], list) else [extracted["important_events"]]:
                    if isinstance(event, str) and event:
                        await self.store_memory(
                            user_id,
                            event,
                            memory_type="episode",
                            importance=0.7,
                            source_session_id=session_id
                        )
                stored["stored"].append("events")
            
            # 存储偏好
            if "preferences" in extracted and extracted["preferences"]:
                for key, value in extracted["preferences"].items() if isinstance(extracted["preferences"], dict) else []:
                    await self.set_preference(
                        user_id,
                        "inferred",
                        key,
                        value,
                        source="inferred"
                    )
                stored["stored"].append("preferences")
            
            return stored
            
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {"extracted": False, "error": str(e)}
    
    # ==================== 综合上下文 ====================
    
    async def get_full_context(self, user_id: str, current_query: str = "") -> Dict[str, Any]:
        """获取完整的用户上下文"""
        profile_summary = await self.get_profile_summary(user_id)
        relationship_context = await self.get_relationship_context(user_id)
        memory_context = await self.get_memory_context(user_id, current_query)
        preferences = await self.get_all_preferences(user_id)
        patterns = await self.get_active_patterns(user_id)
        
        return {
            "profile": profile_summary,
            "relationships": relationship_context,
            "memories": memory_context,
            "preferences": preferences,
            "patterns": [
                {"name": p.pattern_name, "confidence": p.confidence}
                for p in patterns[:5]
            ]
        }
    
    def build_context_prompt(self, context: Dict[str, Any]) -> str:
        """构建上下文提示词"""
        lines = []
        
        # 用户信息
        profile = context.get("profile", {})
        if profile.get("name") and profile["name"] != "用户":
            lines.append(f"用户名称: {profile['name']}")
        if profile.get("occupation"):
            lines.append(f"职业: {profile['occupation']}")
        if profile.get("communication_style"):
            style_map = {
                "formal": "正式",
                "casual": "随意",
                "balanced": "平衡"
            }
            lines.append(f"沟通风格偏好: {style_map.get(profile['communication_style'], profile['communication_style'])}")
        
        # 关系
        if context.get("relationships"):
            lines.append("")
            lines.append(context["relationships"])
        
        # 记忆
        if context.get("memories"):
            lines.append("")
            lines.append(context["memories"])
        
        return "\n".join(lines) if lines else ""
