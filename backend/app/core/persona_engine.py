"""
Jarvis 人格引擎 (Persona Engine)
让AI更像真人一样交流
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random
from enum import Enum


class Emotion(Enum):
    """情感状态"""
    HAPPY = "happy"
    NEUTRAL = "neutral"
    CARING = "caring"
    ENCOURAGING = "encouraging"
    APOLOGETIC = "apologetic"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"


class TimeOfDay(Enum):
    """时间段"""
    EARLY_MORNING = "early_morning"   # 5-7
    MORNING = "morning"               # 7-12
    NOON = "noon"                     # 12-14
    AFTERNOON = "afternoon"           # 14-18
    EVENING = "evening"               # 18-22
    NIGHT = "night"                   # 22-5


class PersonaEngine:
    """人格引擎 - 让Jarvis有温度"""
    
    def __init__(self, user_name: str = "朋友"):
        self.user_name = user_name
        self.conversation_count = 0
        self.last_interaction: Optional[datetime] = None
        self.user_mood: str = "neutral"
        
        # 情感表达映射
        self.emotion_expressions = {
            Emotion.HAPPY: ["😊", "😄", "🌟", "✨"],
            Emotion.NEUTRAL: ["", "👋", "💬"],
            Emotion.CARING: ["🤗", "💝", "☺️", "💫"],
            Emotion.ENCOURAGING: ["💪", "🎯", "⭐", "🌈"],
            Emotion.APOLOGETIC: ["😅", "🙏", "😔"],
            Emotion.EXCITED: ["🎉", "🚀", "🔥", "⚡"],
            Emotion.THOUGHTFUL: ["🤔", "💭", "📝"],
        }
        
        # 时间问候语
        self.time_greetings = {
            TimeOfDay.EARLY_MORNING: [
                "这么早就醒了！{name}，新的一天充满可能 🌅",
                "早起的{name}！今天一定会很棒 ☀️",
            ],
            TimeOfDay.MORNING: [
                "早上好，{name}！准备好迎接今天了吗？ 😊",
                "{name}，美好的一天开始了！ ☀️",
                "早啊{name}！今天有什么计划？",
            ],
            TimeOfDay.NOON: [
                "{name}，中午好！别忘了吃午饭哦 🍚",
                "午安！{name}记得适当休息 ☕",
            ],
            TimeOfDay.AFTERNOON: [
                "下午好，{name}！工作顺利吗？ 💪",
                "{name}，下午时光，来杯咖啡提提神？ ☕",
            ],
            TimeOfDay.EVENING: [
                "晚上好，{name}！忙了一天辛苦了 🌙",
                "{name}，傍晚时分，放松一下吧 ✨",
            ],
            TimeOfDay.NIGHT: [
                "夜深了，{name}还不休息吗？ 🌙",
                "{name}，注意休息，明天又是新的一天 💫",
            ],
        }
        
        # 长时间未聊天的问候
        self.comeback_greetings = [
            "好久不见，{name}！最近怎么样？ 🤗",
            "{name}，想你了！有什么我能帮到你的吗？",
            "终于等到你了，{name}！有什么需要帮忙的？",
        ]
        
        # 鼓励语
        self.encouragements = [
            "你做得很棒！💪",
            "继续加油，你可以的！⭐",
            "相信自己，一切都会好起来的！🌈",
            "有我在，别担心！🤗",
        ]
        
        # 完成任务的回复
        self.task_completions = [
            "✅ 搞定啦！还需要其他帮助吗？",
            "✅ 已经帮你完成了！",
            "✅ 好了！还有什么我能做的？",
        ]
        
        # 道歉语
        self.apologies = [
            "😅 抱歉，这个我暂时做不到，但我会努力学习的！",
            "🙏 不好意思，出了点小问题。让我换个方式试试？",
            "😔 对不起，这次没能帮到你。要不要换个说法再试一次？",
        ]
    
    def get_time_of_day(self) -> TimeOfDay:
        """获取当前时间段"""
        hour = datetime.now().hour
        if 5 <= hour < 7:
            return TimeOfDay.EARLY_MORNING
        elif 7 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 14:
            return TimeOfDay.NOON
        elif 14 <= hour < 18:
            return TimeOfDay.AFTERNOON
        elif 18 <= hour < 22:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT
    
    def get_greeting(self, is_first_interaction: bool = False) -> str:
        """获取问候语"""
        time_of_day = self.get_time_of_day()
        
        # 检查是否长时间未聊天
        if self.last_interaction:
            hours_since_last = (datetime.now() - self.last_interaction).total_seconds() / 3600
            if hours_since_last > 24:
                return random.choice(self.comeback_greetings).format(name=self.user_name)
        
        # 普通时间问候
        if is_first_interaction:
            greetings = self.time_greetings.get(time_of_day, self.time_greetings[TimeOfDay.MORNING])
            return random.choice(greetings).format(name=self.user_name)
        
        return ""
    
    def get_proactive_message(self, context: Dict[str, Any]) -> Optional[str]:
        """
        生成主动消息
        context 包含: weather, schedules, tasks, unread_count 等
        """
        messages = []
        time_of_day = self.get_time_of_day()
        
        # 早晨主动信息
        if time_of_day == TimeOfDay.MORNING:
            # 天气提醒
            if weather := context.get("weather"):
                temp = weather.get("temp")
                if temp and int(temp) < 5:
                    messages.append(f"今天外面{temp}°C，有点冷，记得穿暖和点！🧥")
                elif temp and int(temp) > 30:
                    messages.append(f"今天{temp}°C，挺热的，注意防暑！☀️")
            
            # 日程提醒
            if schedules := context.get("schedules"):
                count = len(schedules)
                if count > 0:
                    messages.append(f"你今天有 {count} 个日程安排哦 📅")
            
            # 待办提醒
            if tasks := context.get("tasks"):
                urgent = [t for t in tasks if t.get("priority") == "high"]
                if urgent:
                    messages.append(f"还有 {len(urgent)} 个重要待办需要处理 📝")
        
        # 午间提醒
        elif time_of_day == TimeOfDay.NOON:
            messages.append("该吃午饭啦！适当休息一下吧 🍚")
        
        # 傍晚提醒
        elif time_of_day == TimeOfDay.EVENING:
            if tasks := context.get("tasks"):
                incomplete = [t for t in tasks if not t.get("completed")]
                if incomplete:
                    messages.append(f"今天还剩 {len(incomplete)} 个任务，要现在处理还是明天再说？")
        
        # 夜间提醒
        elif time_of_day == TimeOfDay.NIGHT:
            hour = datetime.now().hour
            if hour >= 23:
                messages.append("已经很晚了，早点休息对身体好哦 🌙")
        
        return " ".join(messages) if messages else None
    
    def add_emotion(self, text: str, emotion: Emotion = Emotion.NEUTRAL) -> str:
        """给文本添加情感表达"""
        expressions = self.emotion_expressions.get(emotion, [])
        if expressions:
            expr = random.choice(expressions)
            if expr:
                return f"{expr} {text}"
        return text
    
    def get_thinking_message(self) -> str:
        """获取思考中的消息"""
        messages = [
            "🤔 让我想想...",
            "💭 嗯，我来看看...",
            "🔍 正在帮你查找...",
            "⏳ 稍等一下...",
            "📝 好的，我来处理...",
        ]
        return random.choice(messages)
    
    def get_task_completion_message(self) -> str:
        """获取任务完成消息"""
        return random.choice(self.task_completions)
    
    def get_error_message(self, error_type: str = "general") -> str:
        """获取错误/道歉消息"""
        return random.choice(self.apologies)
    
    def get_encouragement(self) -> str:
        """获取鼓励语"""
        return random.choice(self.encouragements)
    
    def detect_user_mood(self, message: str) -> str:
        """
        检测用户情绪
        TODO: 后续可以用情感分析模型
        """
        # 简单的关键词匹配
        negative_words = ["累", "烦", "郁闷", "难过", "焦虑", "压力", "失败", "糟糕", "不开心"]
        positive_words = ["开心", "高兴", "棒", "好", "成功", "完成", "太好了"]
        
        for word in negative_words:
            if word in message:
                return "negative"
        
        for word in positive_words:
            if word in message:
                return "positive"
        
        return "neutral"
    
    def get_empathetic_response(self, user_mood: str) -> Optional[str]:
        """根据用户情绪给出共情回应"""
        responses = {
            "negative": [
                "听起来你好像有点累了，要不要聊聊？ 🤗",
                "感觉你今天不太顺利，有什么我能帮到的吗？",
                "辛苦了！记得给自己一点放松的时间 💝",
            ],
            "positive": [
                "太棒了！看到你开心我也很高兴！ 🎉",
                "真不错！继续保持好心情！ ✨",
            ],
        }
        
        if user_mood in responses:
            return random.choice(responses[user_mood])
        return None
    
    def format_response(
        self, 
        content: str, 
        emotion: Emotion = Emotion.NEUTRAL,
        add_greeting: bool = False,
        is_error: bool = False
    ) -> str:
        """
        格式化最终响应
        """
        parts = []
        
        # 添加问候（如果需要）
        if add_greeting:
            greeting = self.get_greeting(is_first_interaction=self.conversation_count == 0)
            if greeting:
                parts.append(greeting)
                parts.append("")  # 空行分隔
        
        # 主要内容
        if is_error:
            content = self.add_emotion(content, Emotion.APOLOGETIC)
        else:
            content = self.add_emotion(content, emotion)
        
        parts.append(content)
        
        # 更新交互状态
        self.conversation_count += 1
        self.last_interaction = datetime.now()
        
        return "\n".join(parts)
    
    def get_quick_actions(self, time_of_day: Optional[TimeOfDay] = None) -> List[Dict[str, str]]:
        """
        获取推荐的快捷操作
        基于时间和上下文推荐
        """
        if time_of_day is None:
            time_of_day = self.get_time_of_day()
        
        # 基础快捷操作
        base_actions = [
            {"icon": "📅", "label": "今日日程", "action": "查看今天的日程"},
            {"icon": "✅", "label": "待办事项", "action": "查看待办清单"},
            {"icon": "🌤️", "label": "天气", "action": "今天天气怎么样"},
        ]
        
        # 时间相关的推荐
        time_based = {
            TimeOfDay.MORNING: [
                {"icon": "📰", "label": "新闻", "action": "今日新闻摘要"},
                {"icon": "🚗", "label": "路况", "action": "去公司的路况"},
            ],
            TimeOfDay.AFTERNOON: [
                {"icon": "☕", "label": "休息提醒", "action": "设置15分钟后提醒我休息"},
                {"icon": "📊", "label": "工作进度", "action": "今天完成了哪些任务"},
            ],
            TimeOfDay.EVENING: [
                {"icon": "🏃", "label": "运动", "action": "推荐一些运动"},
                {"icon": "🎬", "label": "娱乐", "action": "推荐一部电影"},
            ],
            TimeOfDay.NIGHT: [
                {"icon": "📖", "label": "阅读", "action": "推荐一本书"},
                {"icon": "🌙", "label": "明日计划", "action": "帮我安排明天的日程"},
            ],
        }
        
        actions = base_actions.copy()
        if time_of_day in time_based:
            actions.extend(time_based[time_of_day])
        
        return actions[:6]  # 最多返回6个
    
    def set_user_name(self, name: str):
        """设置用户名"""
        self.user_name = name
    
    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要（用于前端显示）"""
        return {
            "greeting": self.get_greeting(),
            "time_of_day": self.get_time_of_day().value,
            "quick_actions": self.get_quick_actions(),
            "conversation_count": self.conversation_count,
        }


# 全局单例
_persona_engine: Optional[PersonaEngine] = None


def get_persona_engine(user_name: str = "朋友") -> PersonaEngine:
    """获取人格引擎单例"""
    global _persona_engine
    if _persona_engine is None:
        _persona_engine = PersonaEngine(user_name)
    return _persona_engine
