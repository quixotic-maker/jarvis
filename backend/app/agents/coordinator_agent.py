"""主控Agent - 负责任务分解和派发（增强版）"""
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.core.prompt_service import prompt_service

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """主控Agent，负责理解用户意图并分配任务（增强版）"""
    
    # Agent映射表
    AGENT_MAP = {
        "schedule": "ScheduleAgent",
        "info_retrieval": "InfoRetrievalAgent",
        "email": "EmailAgent",
        "weather": "WeatherAgent",
        "news": "NewsAgent",
        "reminder": "ReminderAgent",
        "file": "FileAgent",
        "calculation": "CalculationAgent",
        "translation": "TranslationAgent",
        "summary": "SummaryAgent",
        "task": "TaskAgent",
        "note": "NoteAgent",
        "code": "CodeAgent",
        "meeting": "MeetingAgent",
        "learning": "LearningAgent",
        "travel": "TravelAgent",
        "health": "HealthAgent",
        "recommendation": "RecommendationAgent",
        "data_analysis": "DataAnalysisAgent",
        "contact": "ContactAgent",
        "chat": "ChatAgent",
        "general": "InfoRetrievalAgent"
    }
    
    def __init__(self, db=None):
        super().__init__(
            name="Coordinator",
            description="主控Agent，负责解析用户输入、意图分析和任务分配"
        )
        self.db = db
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户输入并决定任务类型和分配策略
        
        Args:
            input_data: {
                "user_input": "用户的自然语言输入",
                "context": {"对话上下文"},
                "user_profile": {"用户画像"}
            }
            
        Returns:
            {
                "task_type": "任务类型",
                "assigned_agent": "分配的Agent",
                "intent": {...},
                "response": "直接响应（如果是闲聊）"
            }
        """
        user_input = input_data.get("user_input", "")
        context = input_data.get("context", {})
        user_profile = input_data.get("user_profile", {})
        
        # 先进行快速规则匹配
        quick_result = self._quick_intent_match(user_input)
        if quick_result and quick_result.get("confidence", 0) > 0.9:
            return quick_result
        
        # 使用LLM进行深度意图分析
        return await self._deep_intent_analysis(user_input, context, user_profile)
    
    def _quick_intent_match(self, user_input: str) -> Optional[Dict[str, Any]]:
        """快速规则匹配（高置信度场景）"""
        user_lower = user_input.lower().strip()
        
        # 问候语
        greetings = ["你好", "hi", "hello", "早上好", "下午好", "晚上好", "嗨", "在吗"]
        if user_lower in greetings or any(user_lower.startswith(g) for g in greetings):
            return {
                "success": True,
                "task_type": "chat",
                "assigned_agent": "ChatAgent",
                "intent": {"type": "greeting"},
                "confidence": 0.95,
                "response": self._get_greeting_response()
            }
        
        # 天气（高置信度）
        if "天气" in user_input:
            city = self._extract_city(user_input)
            return {
                "success": True,
                "task_type": "weather",
                "assigned_agent": "WeatherAgent",
                "intent": {"type": "weather_query", "city": city},
                "parameters": {"city": city},
                "confidence": 0.95
            }
        
        # 翻译（高置信度）
        if "翻译" in user_input or "translate" in user_lower:
            return {
                "success": True,
                "task_type": "translation",
                "assigned_agent": "TranslationAgent",
                "intent": {"type": "translation"},
                "confidence": 0.95
            }
        
        # 计算（高置信度）
        calc_keywords = ["计算", "等于多少", "求", "算一下"]
        if any(k in user_input for k in calc_keywords) or self._looks_like_math(user_input):
            return {
                "success": True,
                "task_type": "calculation",
                "assigned_agent": "CalculationAgent",
                "intent": {"type": "calculation"},
                "confidence": 0.92
            }
        
        # 日程（高置信度词）
        schedule_high = ["安排一个", "帮我安排", "添加日程", "创建日程"]
        if any(k in user_input for k in schedule_high):
            return {
                "success": True,
                "task_type": "schedule",
                "assigned_agent": "ScheduleAgent",
                "intent": {"type": "create_schedule"},
                "confidence": 0.92
            }
        
        # 提醒（高置信度词）
        reminder_high = ["提醒我", "设置提醒", "设个提醒"]
        if any(k in user_input for k in reminder_high):
            return {
                "success": True,
                "task_type": "reminder",
                "assigned_agent": "ReminderAgent",
                "intent": {"type": "create_reminder"},
                "confidence": 0.92
            }
        
        return None
    
    async def _deep_intent_analysis(
        self, 
        user_input: str, 
        context: Dict,
        user_profile: Dict
    ) -> Dict[str, Any]:
        """使用LLM进行深度意图分析（集成Prompt系统）"""
        
        # 使用新的Prompt系统生成system_prompt
        current_date = datetime.now().strftime('%Y-%m-%d')
        system_prompt = prompt_service.get_agent_system_prompt(
            "coordinator",
            current_date=current_date
        )
        
        context_info = ""
        if context:
            context_info = f"\n对话上下文：{json.dumps(context, ensure_ascii=False)}"
        
        if user_profile:
            context_info += f"\n用户信息：{json.dumps(user_profile, ensure_ascii=False)}"
        
        # 使用Prompt服务构建完整的消息（带Few-shot示例）
        messages = prompt_service.build_messages(
            agent_name="coordinator",
            user_input=user_input,
            use_few_shot=True,
            num_examples=2,
            context=f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}{context_info}"
        )
        
        # 从messages提取system_prompt和user_prompt
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), system_prompt)
        user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else user_input
        
        try:
            response = await self.process_with_llm(user_msg, system_msg)
            
            # 清理JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            
            task_type = result.get("task_type", "chat")
            
            return {
                "success": True,
                "task_type": task_type,
                "assigned_agent": self.AGENT_MAP.get(task_type, "InfoRetrievalAgent"),
                "intent": result.get("intent", {}),
                "parameters": result.get("parameters", {}),
                "confidence": result.get("confidence", 0.7),
                "needs_clarification": result.get("needs_clarification", False),
                "clarification_question": result.get("clarification_question"),
                "implicit_needs": result.get("implicit_needs", [])
            }
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            # 降级到规则匹配
            return self._fallback_intent(user_input)
    
    def _fallback_intent(self, user_input: str) -> Dict[str, Any]:
        """降级的意图匹配"""
        # 任务关键词映射
        keyword_map = {
            "schedule": ["日程", "安排", "约", "预约", "会议时间"],
            "task": ["待办", "任务", "todo", "要做", "完成"],
            "reminder": ["提醒", "别忘了", "记得"],
            "email": ["邮件", "email", "发送给"],
            "weather": ["天气", "下雨", "温度", "气温"],
            "news": ["新闻", "资讯", "最新消息"],
            "translation": ["翻译", "translate", "用英语", "用中文"],
            "calculation": ["计算", "等于", "加", "减", "乘", "除", "求"],
            "code": ["代码", "编程", "python", "javascript", "函数", "算法"],
            "note": ["笔记", "记录", "note", "记下"],
            "meeting": ["会议", "开会", "会议纪要"],
            "travel": ["旅行", "旅游", "出行", "出差", "攻略"],
            "health": ["健康", "运动", "锻炼", "睡眠", "饮食"],
            "recommendation": ["推荐", "建议", "有什么好的"],
            "info_retrieval": ["什么是", "是什么", "怎么", "如何", "为什么"],
            "contact": ["联系人", "电话", "联系方式"]
        }
        
        user_lower = user_input.lower()
        
        for task_type, keywords in keyword_map.items():
            if any(kw in user_lower for kw in keywords):
                return {
                    "success": True,
                    "task_type": task_type,
                    "assigned_agent": self.AGENT_MAP.get(task_type, "InfoRetrievalAgent"),
                    "intent": {"type": task_type},
                    "confidence": 0.6
                }
        
        # 默认为闲聊/信息查询
        return {
            "success": True,
            "task_type": "chat",
            "assigned_agent": "ChatAgent",
            "intent": {"type": "general"},
            "confidence": 0.5
        }
    
    def _get_greeting_response(self) -> str:
        """获取问候响应"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        else:
            time_greeting = "晚上好"
        
        return f"{time_greeting}！我是Jarvis，有什么我可以帮你的吗？"
    
    def _extract_city(self, text: str) -> str:
        """从文本中提取城市名"""
        # 常见城市列表
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
            "武汉", "西安", "重庆", "天津", "青岛", "大连", "厦门", "宁波"
        ]
        
        for city in cities:
            if city in text:
                return city
        
        return "北京"  # 默认城市
    
    def _looks_like_math(self, text: str) -> bool:
        """判断是否像数学表达式"""
        math_patterns = ["+", "-", "*", "×", "÷", "/", "=", "^", "²", "³"]
        # 检查是否包含数学符号和数字
        has_number = any(c.isdigit() for c in text)
        has_operator = any(op in text for op in math_patterns)
        return has_number and has_operator


# 为了兼容性，保留Coordinator别名
Coordinator = CoordinatorAgent

