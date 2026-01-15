"""
对话服务核心 - Jarvis的灵魂

负责：
- 管理对话会话
- 协调意图识别
- 调用Agent执行任务
- 生成自然语言回复
- 人格化交互
"""
import json
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from app.db.models import Session, Message
from app.core.memory import MemoryManager
from app.core.config import settings
from app.core.persona_engine import get_persona_engine, Emotion

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """对话响应"""
    session_id: str
    message_id: int
    content: str
    intent: str
    intent_confidence: float
    agent_used: Optional[str] = None
    action_result: Optional[Dict] = None
    suggestions: Optional[List[str]] = None
    emotion_detected: Optional[str] = None
    response_time_ms: int = 0


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: str  # chat, query, action, status, system
    confidence: float
    action_type: Optional[str] = None  # schedule, reminder, email, etc.
    entities: Optional[Dict] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


class ChatService:
    """对话服务核心"""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.memory_manager = MemoryManager(db)
        self.llm_enabled = bool(settings.DEEPSEEK_API_KEY)
        self._agents = None  # 延迟加载
        self.persona = get_persona_engine()  # 人格引擎
    
    @property
    def agents(self):
        """延迟加载Agent"""
        if self._agents is None:
            self._agents = self._load_agents()
        return self._agents
    
    def _load_agents(self) -> Dict:
        """加载所有Agent"""
        from app.agents.coordinator_agent import CoordinatorAgent
        from app.agents.schedule_agent import ScheduleAgent
        from app.agents.task_agent import TaskAgent
        from app.agents.email_agent import EmailAgent
        from app.agents.weather_agent import WeatherAgent
        from app.agents.reminder_agent import ReminderAgent
        from app.agents.info_agent import InfoRetrievalAgent
        from app.agents.translation_agent import TranslationAgent
        from app.agents.summary_agent import SummaryAgent
        from app.agents.calculation_agent import CalculationAgent
        from app.agents.code_agent import CodeAgent
        from app.agents.note_agent import NoteAgent
        from app.agents.news_agent import NewsAgent
        from app.agents.travel_agent import TravelAgent
        from app.agents.health_agent import HealthAgent
        from app.agents.recommendation_agent import RecommendationAgent
        from app.agents.mcp_agent import MCPAgent
        from app.agents.map_agent import MapAgent
        
        return {
            "coordinator": CoordinatorAgent(self.db),
            "schedule": ScheduleAgent(),
            "task": TaskAgent(),
            "email": EmailAgent(),
            "weather": WeatherAgent(),
            "reminder": ReminderAgent(),
            "info": InfoRetrievalAgent(),
            "translation": TranslationAgent(),
            "summary": SummaryAgent(),
            "calculation": CalculationAgent(),
            "code": CodeAgent(),
            "note": NoteAgent(),
            "news": NewsAgent(),
            "travel": TravelAgent(),
            "health": HealthAgent(),
            "recommendation": RecommendationAgent(),
            "mcp": MCPAgent(),
            "map": MapAgent(),
        }
    
    # ==================== 会话管理 ====================
    
    async def get_or_create_session(
        self, 
        session_id: Optional[str], 
        user_id: str
    ) -> Session:
        """获取或创建会话"""
        if session_id:
            session = self.db.query(Session).filter(
                Session.id == session_id
            ).first()
            if session:
                return session
        
        # 创建新会话
        new_session = Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title="新对话"
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        
        logger.info(f"Created new session: {new_session.id}")
        return new_session
    
    async def get_sessions(
        self, 
        user_id: str, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> List[Session]:
        """获取用户的会话列表"""
        query = self.db.query(Session).filter(Session.user_id == user_id)
        
        if not include_inactive:
            query = query.filter(Session.is_active == True)
        
        return query.order_by(desc(Session.last_activity)).limit(limit).all()
    
    async def get_session_messages(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[Message]:
        """获取会话的消息历史"""
        return self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).limit(limit).all()
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        session = self.db.query(Session).filter(Session.id == session_id).first()
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
    
    # ==================== 核心对话处理 ====================
    
    async def chat(
        self, 
        user_id: str, 
        message: str,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """处理用户消息 - 核心方法"""
        start_time = time.time()
        
        # 1. 获取或创建会话
        session = await self.get_or_create_session(session_id, user_id)
        
        # 2. 保存用户消息
        user_message = await self._save_message(session.id, "user", message)
        
        # 3. 加载用户上下文
        user_context = await self.memory_manager.get_full_context(user_id, message)
        
        # 4. 获取对话历史
        conversation_history = await self._get_conversation_history(session.id)
        
        # 5. 分析意图
        intent_result = await self._analyze_intent(message, user_context, conversation_history)
        
        # 6. 检测情绪
        emotion = await self._detect_emotion(message)
        
        # 7. 根据意图处理
        response_content, action_result, agent_used = await self._process_by_intent(
            message, intent_result, user_context, conversation_history
        )
        
        # 8. 生成建议（快捷操作）
        suggestions = await self._generate_suggestions(intent_result, action_result)
        
        # 9. 保存助手回复
        response_time = int((time.time() - start_time) * 1000)
        assistant_message = await self._save_message(
            session.id, "assistant", response_content,
            intent=intent_result.intent,
            intent_confidence=intent_result.confidence,
            agent_used=agent_used,
            action_result=action_result,
            emotion=emotion,
            response_time_ms=response_time
        )
        
        # 10. 更新会话信息
        await self._update_session(session, message)
        
        # 11. 异步提取并存储记忆（不阻塞响应）
        try:
            await self.memory_manager.extract_and_store_information(
                user_id, message, response_content, session.id
            )
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
        
        return ChatResponse(
            session_id=session.id,
            message_id=assistant_message.id,
            content=response_content,
            intent=intent_result.intent,
            intent_confidence=intent_result.confidence,
            agent_used=agent_used,
            action_result=action_result,
            suggestions=suggestions,
            emotion_detected=emotion,
            response_time_ms=response_time
        )
    
    # ==================== 流式对话处理 ====================
    
    async def chat_stream(
        self, 
        user_id: str, 
        message: str,
        session_id: Optional[str] = None
    ):
        """流式处理用户消息 - 实时输出"""
        from typing import AsyncGenerator
        
        start_time = time.time()
        
        # 1. 获取或创建会话
        session = await self.get_or_create_session(session_id, user_id)
        
        # 发送会话信息
        yield {"type": "session", "session_id": session.id}
        
        # 2. 保存用户消息
        user_message = await self._save_message(session.id, "user", message)
        
        # 3. 加载用户上下文
        user_context = await self.memory_manager.get_full_context(user_id, message)
        
        # 4. 获取对话历史
        conversation_history = await self._get_conversation_history(session.id)
        
        # 5. 分析意图
        yield {"type": "thinking", "content": "正在分析..."}
        intent_result = await self._analyze_intent(message, user_context, conversation_history)
        
        yield {"type": "intent", "intent": intent_result.intent, "action_type": intent_result.action_type}
        
        # 6. 检测情绪
        emotion = await self._detect_emotion(message)
        
        # 7. 根据意图类型决定处理方式
        if intent_result.intent == "chat":
            # 闲聊 - 流式输出
            full_content = ""
            async for chunk in self._stream_chat_response(message, user_context, conversation_history):
                full_content += chunk
                yield {"type": "content", "content": chunk}
            response_content = full_content
            action_result = None
            agent_used = None
        else:
            # 执行任务 - 非流式
            response_content, action_result, agent_used = await self._process_by_intent(
                message, intent_result, user_context, conversation_history
            )
            yield {"type": "content", "content": response_content}
        
        # 8. 生成建议
        suggestions = await self._generate_suggestions(intent_result, action_result)
        
        # 9. 保存助手回复
        response_time = int((time.time() - start_time) * 1000)
        assistant_message = await self._save_message(
            session.id, "assistant", response_content,
            intent=intent_result.intent,
            intent_confidence=intent_result.confidence,
            agent_used=agent_used,
            action_result=action_result,
            emotion=emotion,
            response_time_ms=response_time
        )
        
        # 10. 更新会话
        await self._update_session(session, message)
        
        # 11. 发送完成信息
        yield {
            "type": "complete",
            "message_id": assistant_message.id,
            "intent": intent_result.intent,
            "agent_used": agent_used,
            "action_result": action_result,
            "suggestions": suggestions,
            "emotion": emotion,
            "response_time_ms": response_time
        }
        
        # 12. 异步存储记忆
        try:
            await self.memory_manager.extract_and_store_information(
                user_id, message, response_content, session.id
            )
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
    
    async def _stream_chat_response(
        self, 
        message: str, 
        user_context: Dict,
        conversation_history: List[Dict]
    ):
        """流式生成聊天响应"""
        if not self.llm_enabled:
            yield "你好！有什么我可以帮你的吗？"
            return
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            
            # 构建系统提示
            profile = user_context.get("profile", {})
            style = profile.get("communication_style", "balanced")
            name = profile.get("name")
            
            style_instruction = {
                "formal": "保持专业、正式的语气",
                "casual": "用轻松、友好的语气，可以使用表情",
                "balanced": "保持友好但专业的语气"
            }.get(style, "保持友好但专业的语气")
            
            context_prompt = self.memory_manager.build_context_prompt(user_context)
            
            system_prompt = f"""你是Jarvis，一个智能私人助手。{style_instruction}。

{f'用户叫{name}，' if name else ''}你应该：
1. 自然、亲切地交流
2. 记住用户之前说过的事情
3. 在合适的时候提供帮助建议
4. 支持Markdown格式输出，代码用代码块，列表用列表格式

{f'用户背景信息：{context_prompt}' if context_prompt else ''}"""

            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in conversation_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})
            
            # 流式调用API
            response = client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True  # 启用流式输出
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in stream chat: {e}")
            yield "抱歉，我现在有点问题。有什么我可以帮你的吗？"
    
    # ==================== 意图分析 ====================
    
    async def _analyze_intent(
        self, 
        message: str, 
        user_context: Dict,
        conversation_history: List[Dict]
    ) -> IntentResult:
        """分析用户意图"""
        
        if not self.llm_enabled:
            return self._rule_based_intent(message)
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            
            # 构建上下文
            context_prompt = self.memory_manager.build_context_prompt(user_context)
            history_text = self._format_history(conversation_history[-5:])  # 最近5轮对话
            
            system_prompt = """你是意图分析专家。分析用户消息，识别意图类型。

意图类型：
- chat: 闲聊、问候、情感表达、一般性交谈
- query: 信息查询、知识问答、状态查询
- action: 需要执行任务（创建日程、设置提醒、发邮件、翻译、计算等）
- status: 查询任务状态、进度
- system: 系统设置、偏好调整

任务子类型（当intent=action时）：
- schedule: 日程安排
- reminder: 提醒设置
- task: 待办事项
- email: 邮件相关
- weather: 天气查询
- translation: 翻译
- calculation: 计算
- code: 代码相关
- note: 笔记相关
- news: 新闻资讯
- travel: 旅行规划
- health: 健康建议
- recommendation: 推荐

返回严格的JSON格式：
{
    "intent": "意图类型",
    "confidence": 0.95,
    "action_type": "任务子类型（仅action时需要）",
    "entities": {"提取的实体，如时间、地点、人物等"},
    "needs_clarification": false,
    "clarification_question": "需要追问的问题（如果需要）"
}

注意：
1. 只返回JSON，不要其他内容
2. confidence必须是0-1的小数
3. 如果信息不足以执行任务，设置needs_clarification=true"""

            user_prompt = f"""用户上下文：
{context_prompt if context_prompt else "（新用户，无历史信息）"}

最近对话：
{history_text if history_text else "（新对话）"}

当前用户消息：{message}

请分析意图并返回JSON："""

            response = client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 清理JSON
            if "```" in result_text:
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            
            return IntentResult(
                intent=result.get("intent", "chat"),
                confidence=result.get("confidence", 0.8),
                action_type=result.get("action_type"),
                entities=result.get("entities"),
                needs_clarification=result.get("needs_clarification", False),
                clarification_question=result.get("clarification_question")
            )
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return self._rule_based_intent(message)
    
    def _rule_based_intent(self, message: str) -> IntentResult:
        """基于规则的意图识别（备用）"""
        message_lower = message.lower()
        
        # 问候
        greetings = ["你好", "hi", "hello", "早上好", "下午好", "晚上好", "嗨"]
        if any(g in message_lower for g in greetings):
            return IntentResult(intent="chat", confidence=0.9)
        
        # 日程
        schedule_keywords = ["安排", "日程", "会议", "约", "提醒我"]
        if any(k in message for k in schedule_keywords):
            return IntentResult(
                intent="action", 
                confidence=0.8, 
                action_type="schedule"
            )
        
        # 任务
        task_keywords = ["待办", "任务", "todo", "要做"]
        if any(k in message_lower for k in task_keywords):
            return IntentResult(
                intent="action", 
                confidence=0.8, 
                action_type="task"
            )
        
        # 天气
        if "天气" in message:
            return IntentResult(
                intent="action", 
                confidence=0.9, 
                action_type="weather"
            )
        
        # 翻译
        if "翻译" in message or "translate" in message_lower:
            return IntentResult(
                intent="action", 
                confidence=0.9, 
                action_type="translation"
            )
        
        # 计算
        if "计算" in message or "等于" in message or any(op in message for op in ["+", "-", "*", "×", "÷"]):
            return IntentResult(
                intent="action", 
                confidence=0.8, 
                action_type="calculation"
            )
        
        # 代码
        code_keywords = ["代码", "编程", "python", "javascript", "函数", "写一个"]
        if any(k in message_lower for k in code_keywords):
            return IntentResult(
                intent="action", 
                confidence=0.8, 
                action_type="code"
            )
        
        # 查询类
        query_keywords = ["是什么", "什么是", "怎么", "如何", "为什么", "查询", "查一下", "告诉我"]
        if any(k in message for k in query_keywords):
            return IntentResult(intent="query", confidence=0.7)
        
        # 默认为闲聊
        return IntentResult(intent="chat", confidence=0.6)
    
    # ==================== 意图处理 ====================
    
    async def _process_by_intent(
        self,
        message: str,
        intent_result: IntentResult,
        user_context: Dict,
        conversation_history: List[Dict]
    ) -> Tuple[str, Optional[Dict], Optional[str]]:
        """根据意图处理消息"""
        
        # 需要澄清
        if intent_result.needs_clarification:
            return intent_result.clarification_question, None, None
        
        intent = intent_result.intent
        action_type = intent_result.action_type
        
        # 闲聊
        if intent == "chat":
            response = await self._handle_chat(message, user_context, conversation_history)
            return response, None, None
        
        # 信息查询
        if intent == "query":
            response, result = await self._handle_query(message, user_context)
            return response, result, "info"
        
        # 执行任务
        if intent == "action":
            return await self._handle_action(message, action_type, intent_result.entities)
        
        # 状态查询
        if intent == "status":
            response, result = await self._handle_status(message)
            return response, result, None
        
        # 系统设置
        if intent == "system":
            response = await self._handle_system(message)
            return response, None, None
        
        # 默认处理
        return await self._handle_chat(message, user_context, conversation_history), None, None
    
    async def _handle_chat(
        self, 
        message: str, 
        user_context: Dict,
        conversation_history: List[Dict]
    ) -> str:
        """处理闲聊"""
        
        if not self.llm_enabled:
            return "你好！有什么我可以帮你的吗？"
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            
            # 获取用户偏好
            profile = user_context.get("profile", {})
            style = profile.get("communication_style", "balanced")
            name = profile.get("name")
            
            style_instruction = {
                "formal": "保持专业、正式的语气",
                "casual": "用轻松、友好的语气，可以使用表情",
                "balanced": "保持友好但专业的语气"
            }.get(style, "保持友好但专业的语气")
            
            context_prompt = self.memory_manager.build_context_prompt(user_context)
            
            system_prompt = f"""你是Jarvis，一个智能私人助手。{style_instruction}。

{f'用户叫{name}，' if name else ''}你应该：
1. 自然、亲切地交流
2. 记住用户之前说过的事情
3. 在合适的时候提供帮助建议
4. 回复简洁但有温度

{f'用户背景信息：{context_prompt}' if context_prompt else ''}"""

            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "抱歉，我现在有点问题。有什么我可以帮你的吗？"
    
    async def _handle_query(
        self, 
        message: str, 
        user_context: Dict
    ) -> Tuple[str, Optional[Dict]]:
        """处理信息查询"""
        try:
            result = await self.agents["info"].execute({"user_input": message, "query": message})
            return result.get("answer", "抱歉，我没有找到相关信息。"), result
        except Exception as e:
            logger.error(f"Error in query: {e}")
            return "抱歉，查询时遇到了问题。", None
    
    async def _handle_action(
        self, 
        message: str, 
        action_type: str,
        entities: Optional[Dict]
    ) -> Tuple[str, Optional[Dict], Optional[str]]:
        """处理任务执行"""
        
        agent_map = {
            "schedule": "schedule",
            "reminder": "reminder",
            "task": "task",
            "email": "email",
            "weather": "weather",
            "translation": "translation",
            "calculation": "calculation",
            "code": "code",
            "note": "note",
            "news": "news",
            "travel": "travel",
            "health": "health",
            "recommendation": "recommendation"
        }
        
        agent_name = agent_map.get(action_type)
        
        if not agent_name or agent_name not in self.agents:
            # 使用coordinator分配
            try:
                result = await self.agents["coordinator"].execute({
                    "user_input": message,
                    "context": {},
                    "user_profile": {}
                })
                return result.get("response", "好的，我已处理。"), result, "coordinator"
            except Exception as e:
                logger.error(f"Coordinator error: {e}")
                return "抱歉，我无法处理这个请求。", None, None
        
        try:
            agent = self.agents[agent_name]
            result = await agent.execute({
                "user_input": message,
                "action": "create",
                "db": self.db
            })
            
            # 生成自然语言响应
            response = self._format_action_response(action_type, result)
            
            return response, result, agent_name
            
        except Exception as e:
            logger.error(f"Error executing {action_type}: {e}")
            return f"抱歉，执行{action_type}任务时遇到了问题。", None, agent_name
    
    async def _handle_status(self, message: str) -> Tuple[str, Optional[Dict]]:
        """处理状态查询"""
        # TODO: 实现状态查询逻辑
        return "让我查一下...", None
    
    async def _handle_system(self, message: str) -> str:
        """处理系统设置"""
        # TODO: 实现系统设置逻辑
        return "系统设置功能正在开发中。"
    
    def _format_action_response(self, action_type: str, result: Dict) -> str:
        """格式化任务执行响应"""
        if not result.get("success", True):
            return result.get("message", result.get("error", "执行任务时遇到了问题。"))
        
        # 根据不同任务类型格式化响应
        if action_type == "schedule":
            if "schedule" in result:
                s = result["schedule"]
                return f"✅ 好的，已为您安排日程：\n\n📅 **{s.get('title', '日程')}**\n⏰ 时间：{s.get('start_time', '')}\n📍 地点：{s.get('location', '未设置')}"
            return result.get("message", "日程已创建。")
        
        if action_type == "reminder":
            r = result.get("reminder", {})
            if r:
                return f"✅ 提醒已设置！\n\n⏰ **{r.get('content', '提醒')}**\n📅 时间：{r.get('remind_at', '')}"
            return result.get("message", "提醒已设置。")
        
        if action_type == "weather":
            weather = result.get("weather", {})
            if weather:
                current = weather.get("current", {})
                forecast = weather.get("forecast", [])
                location = weather.get("location", "未知")
                
                response = f"## 🌤️ {location}天气\n\n"
                response += f"### 当前天气\n"
                response += f"- 🌡️ 温度：**{current.get('temperature', '--')}°C**（体感 {current.get('feels_like', '--')}°C）\n"
                response += f"- ☁️ 天气：{current.get('condition', '--')}\n"
                response += f"- 💧 湿度：{current.get('humidity', '--')}%\n"
                response += f"- 🌬️ 风：{current.get('wind_dir', '')} {current.get('wind_speed', '')}km/h\n\n"
                
                if forecast:
                    response += "### 未来天气预报\n\n"
                    response += "| 日期 | 白天 | 夜间 | 温度 |\n"
                    response += "|------|------|------|------|\n"
                    for day in forecast[:3]:
                        response += f"| {day.get('date', '')} | {day.get('condition_day', day.get('condition', ''))} | {day.get('condition_night', '--')} | {day.get('low', '--')}~{day.get('high', '--')}°C |\n"
                
                suggestion = weather.get("suggestion", "")
                if suggestion:
                    response += f"\n### 💡 建议\n{suggestion}\n"
                
                source = result.get("source", "")
                if source:
                    response += f"\n---\n*数据来源：{source}*"
                
                return response
            return result.get("message", "天气信息获取失败")
        
        if action_type == "news":
            news_list = result.get("news", [])
            if news_list:
                category_names = {
                    "technology": "科技",
                    "business": "财经",
                    "entertainment": "娱乐",
                    "sports": "体育",
                    "health": "健康",
                    "science": "科学",
                    "general": "综合"
                }
                cat = category_names.get(result.get("category", "general"), "综合")
                
                response = f"## 📰 {cat}新闻\n\n"
                for i, news in enumerate(news_list, 1):
                    title = news.get("title", "无标题")
                    desc = news.get("description", "")
                    source = news.get("source", "")
                    response += f"### {i}. {title}\n"
                    if desc:
                        response += f"{desc}\n"
                    if source:
                        response += f"*来源：{source}*\n"
                    response += "\n"
                
                api_source = result.get("source", "")
                if api_source:
                    response += f"---\n*数据来源：{api_source}*"
                
                return response
            return result.get("message", "暂无新闻")
        
        if action_type == "translation":
            translation = result.get("translation", "")
            original = result.get("original", "")
            if translation:
                return f"## 🌐 翻译结果\n\n**原文：** {original}\n\n**译文：** {translation}"
            return result.get("message", "翻译完成")
        
        if action_type == "calculation":
            calc_result = result.get("result", "")
            expression = result.get("expression", "")
            if calc_result:
                return f"## 🔢 计算结果\n\n**表达式：** `{expression}`\n\n**结果：** **{calc_result}**"
            return f"计算结果：{result.get('message', '')}"
        
        if action_type == "code":
            code = result.get("code", "")
            language = result.get("language", "python")
            explanation = result.get("explanation", "")
            if code:
                response = ""
                if explanation:
                    response += f"{explanation}\n\n"
                response += f"```{language}\n{code}\n```"
                return response
            return result.get("message", "代码生成完成")
        
        # 默认响应
        return result.get("message", result.get("response", "任务已完成。"))
    
    # ==================== 辅助方法 ====================
    
    async def _detect_emotion(self, message: str) -> Optional[str]:
        """检测用户情绪"""
        # 简单的关键词检测
        positive = ["开心", "高兴", "太好了", "棒", "谢谢", "感谢", "哈哈", "😊", "🎉"]
        negative = ["烦", "累", "郁闷", "难过", "生气", "焦虑", "压力", "😢", "😤"]
        
        message_lower = message.lower()
        
        if any(p in message for p in positive):
            return "positive"
        if any(n in message for n in negative):
            return "negative"
        
        return "neutral"
    
    async def _generate_suggestions(
        self, 
        intent_result: IntentResult,
        action_result: Optional[Dict]
    ) -> List[str]:
        """生成后续建议"""
        suggestions = []
        
        if intent_result.intent == "action":
            if intent_result.action_type == "schedule":
                suggestions = ["添加提醒", "邀请参会人", "查看今日日程"]
            elif intent_result.action_type == "task":
                suggestions = ["查看待办列表", "设置提醒", "标记完成"]
            elif intent_result.action_type == "email":
                suggestions = ["修改内容", "添加附件", "发送邮件"]
        
        elif intent_result.intent == "chat":
            suggestions = ["查看日程", "设置提醒", "有什么可以帮你？"]
        
        return suggestions[:3]
    
    async def _save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        **kwargs
    ) -> Message:
        """保存消息"""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            **kwargs
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def _update_session(self, session: Session, last_message: str):
        """更新会话信息"""
        session.last_activity = datetime.utcnow()
        session.message_count += 1
        
        # 如果是新会话，生成标题
        if session.title == "新对话" and session.message_count >= 2:
            session.title = last_message[:30] + ("..." if len(last_message) > 30 else "")
        
        self.db.commit()
    
    async def _get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """获取对话历史"""
        messages = await self.get_session_messages(session_id, limit)
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化对话历史"""
        if not history:
            return ""
        
        lines = []
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(lines)
