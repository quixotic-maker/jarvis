"""
主动智能服务 - Jarvis的主动关怀

负责：
- 时间触发的主动服务（早晨问候、日程提醒等）
- 状态触发的主动服务（任务堆积警告等）
- 情景触发的主动服务（出差准备等）
- 智能推荐
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_, or_

from app.db.models import (
    UserProfile, UserMemory, BehaviorPattern, 
    ProactiveTask, Schedule, Reminder, TodoItem
)
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ProactiveNotification:
    """主动通知"""
    notification_type: str  # greeting, reminder, suggestion, alert
    title: str
    content: str
    priority: int  # 1-5
    action_data: Optional[Dict] = None
    suggestions: Optional[List[str]] = None


class ProactiveService:
    """主动智能服务"""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.llm_enabled = bool(settings.DEEPSEEK_API_KEY)
    
    # ==================== 主动服务入口 ====================
    
    async def get_proactive_notifications(
        self, 
        user_id: str
    ) -> List[ProactiveNotification]:
        """获取用户的主动通知"""
        notifications = []
        
        # 1. 时间相关通知
        time_notifications = await self._get_time_based_notifications(user_id)
        notifications.extend(time_notifications)
        
        # 2. 日程相关通知
        schedule_notifications = await self._get_schedule_notifications(user_id)
        notifications.extend(schedule_notifications)
        
        # 3. 任务相关通知
        task_notifications = await self._get_task_notifications(user_id)
        notifications.extend(task_notifications)
        
        # 4. 智能推荐
        recommendations = await self._get_recommendations(user_id)
        notifications.extend(recommendations)
        
        # 按优先级排序
        notifications.sort(key=lambda x: x.priority, reverse=True)
        
        return notifications[:5]  # 最多返回5个通知
    
    # ==================== 时间触发通知 ====================
    
    async def _get_time_based_notifications(
        self, 
        user_id: str
    ) -> List[ProactiveNotification]:
        """获取时间相关的通知"""
        notifications = []
        now = datetime.now()
        hour = now.hour
        
        # 获取用户档案
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        # 早晨问候（工作日的工作开始时间）
        if profile and profile.work_start_hour <= hour < profile.work_start_hour + 1:
            if now.weekday() < 5:  # 工作日
                greeting = await self._generate_morning_greeting(user_id, profile)
                if greeting:
                    notifications.append(greeting)
        
        # 下班提醒
        if profile and profile.work_end_hour <= hour < profile.work_end_hour + 1:
            if now.weekday() < 5:
                evening_notification = await self._generate_evening_summary(user_id)
                if evening_notification:
                    notifications.append(evening_notification)
        
        return notifications
    
    async def _generate_morning_greeting(
        self, 
        user_id: str, 
        profile: UserProfile
    ) -> Optional[ProactiveNotification]:
        """生成早晨问候"""
        
        # 获取今日日程
        today = datetime.now().date()
        schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.start_time >= datetime.combine(today, datetime.min.time()),
                Schedule.start_time < datetime.combine(today, datetime.max.time()),
                Schedule.is_completed == False
            )
        ).order_by(Schedule.start_time).all()
        
        # 获取待办事项
        todos = self.db.query(TodoItem).filter(
            and_(
                TodoItem.is_completed == False,
                or_(
                    TodoItem.due_date == None,
                    TodoItem.due_date >= today
                )
            )
        ).limit(5).all()
        
        # 构建问候内容
        name = profile.name or "主人"
        
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        else:
            time_greeting = "晚上好"
        
        content_parts = [f"{time_greeting}，{name}！"]
        
        if schedules:
            content_parts.append(f"\n📅 今天有 {len(schedules)} 个日程安排")
            # 最近的日程
            next_schedule = schedules[0]
            time_str = next_schedule.start_time.strftime("%H:%M")
            content_parts.append(f"   ⏰ {time_str} {next_schedule.title}")
        else:
            content_parts.append("\n📅 今天没有日程安排，轻松一天~")
        
        if todos:
            content_parts.append(f"\n📝 有 {len(todos)} 个待办事项")
        
        return ProactiveNotification(
            notification_type="greeting",
            title="早安问候",
            content="\n".join(content_parts),
            priority=3,
            suggestions=["查看今日详情", "添加新日程", "设置提醒"]
        )
    
    async def _generate_evening_summary(
        self, 
        user_id: str
    ) -> Optional[ProactiveNotification]:
        """生成晚间总结"""
        
        today = datetime.now().date()
        
        # 今日完成的任务
        completed_todos = self.db.query(TodoItem).filter(
            and_(
                TodoItem.is_completed == True,
                TodoItem.updated_at >= datetime.combine(today, datetime.min.time())
            )
        ).count()
        
        # 今日完成的日程
        completed_schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.is_completed == True,
                Schedule.start_time >= datetime.combine(today, datetime.min.time()),
                Schedule.start_time < datetime.combine(today, datetime.max.time())
            )
        ).count()
        
        content_parts = ["辛苦了！今天的工作告一段落。"]
        
        if completed_todos > 0 or completed_schedules > 0:
            content_parts.append(f"\n✅ 今日完成: {completed_todos} 个任务, {completed_schedules} 个日程")
        
        # 检查明天的日程
        tomorrow = today + timedelta(days=1)
        tomorrow_schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.start_time >= datetime.combine(tomorrow, datetime.min.time()),
                Schedule.start_time < datetime.combine(tomorrow, datetime.max.time()),
                Schedule.is_completed == False
            )
        ).count()
        
        if tomorrow_schedules > 0:
            content_parts.append(f"\n📅 明天有 {tomorrow_schedules} 个安排")
        
        return ProactiveNotification(
            notification_type="summary",
            title="今日总结",
            content="\n".join(content_parts),
            priority=2,
            suggestions=["查看明日安排", "设置明日提醒"]
        )
    
    # ==================== 日程触发通知 ====================
    
    async def _get_schedule_notifications(
        self, 
        user_id: str
    ) -> List[ProactiveNotification]:
        """获取日程相关通知"""
        notifications = []
        now = datetime.now()
        
        # 即将开始的日程（15分钟内）
        upcoming_time = now + timedelta(minutes=15)
        upcoming_schedules = self.db.query(Schedule).filter(
            and_(
                Schedule.start_time > now,
                Schedule.start_time <= upcoming_time,
                Schedule.is_completed == False,
                Schedule.reminder_sent == False
            )
        ).all()
        
        for schedule in upcoming_schedules:
            minutes_left = int((schedule.start_time - now).total_seconds() / 60)
            
            notifications.append(ProactiveNotification(
                notification_type="reminder",
                title="日程即将开始",
                content=f"📅 {schedule.title}\n⏰ {minutes_left} 分钟后开始" + 
                       (f"\n📍 {schedule.location}" if schedule.location else ""),
                priority=5,
                action_data={"schedule_id": schedule.id, "type": "schedule"},
                suggestions=["查看详情", "推迟15分钟", "标记完成"]
            ))
            
            # 标记已发送
            schedule.reminder_sent = True
        
        self.db.commit()
        
        return notifications
    
    # ==================== 任务触发通知 ====================
    
    async def _get_task_notifications(
        self, 
        user_id: str
    ) -> List[ProactiveNotification]:
        """获取任务相关通知"""
        notifications = []
        now = datetime.now()
        today = now.date()
        
        # 即将到期的任务（今天到期）
        due_today = self.db.query(TodoItem).filter(
            and_(
                TodoItem.is_completed == False,
                TodoItem.due_date >= datetime.combine(today, datetime.min.time()),
                TodoItem.due_date < datetime.combine(today, datetime.max.time())
            )
        ).all()
        
        if due_today:
            task_names = [t.title for t in due_today[:3]]
            more = f" 等{len(due_today)}项" if len(due_today) > 3 else ""
            
            notifications.append(ProactiveNotification(
                notification_type="alert",
                title="今日截止任务",
                content=f"⚠️ 以下任务今天到期:\n" + "\n".join(f"• {t}" for t in task_names) + more,
                priority=4,
                suggestions=["查看全部", "开始处理", "延期"]
            ))
        
        # 过期任务
        overdue = self.db.query(TodoItem).filter(
            and_(
                TodoItem.is_completed == False,
                TodoItem.due_date < datetime.combine(today, datetime.min.time())
            )
        ).count()
        
        if overdue > 0:
            notifications.append(ProactiveNotification(
                notification_type="alert",
                title="过期任务提醒",
                content=f"📌 您有 {overdue} 个过期任务需要处理",
                priority=4,
                suggestions=["查看过期任务", "批量处理"]
            ))
        
        # 高优先级未完成任务
        high_priority = self.db.query(TodoItem).filter(
            and_(
                TodoItem.is_completed == False,
                TodoItem.priority == "high"
            )
        ).count()
        
        if high_priority >= 3:
            notifications.append(ProactiveNotification(
                notification_type="suggestion",
                title="高优先级任务",
                content=f"💡 您有 {high_priority} 个高优先级任务，建议优先处理",
                priority=3,
                suggestions=["查看高优先级任务", "安排工作计划"]
            ))
        
        return notifications
    
    # ==================== 智能推荐 ====================
    
    async def _get_recommendations(
        self, 
        user_id: str
    ) -> List[ProactiveNotification]:
        """获取智能推荐"""
        notifications = []
        
        # 获取用户行为模式
        patterns = self.db.query(BehaviorPattern).filter(
            and_(
                BehaviorPattern.user_id == user_id,
                BehaviorPattern.is_active == True,
                BehaviorPattern.confidence >= 0.7
            )
        ).order_by(BehaviorPattern.confidence.desc()).limit(3).all()
        
        # 根据行为模式生成推荐
        for pattern in patterns:
            if pattern.pattern_type == "time_based":
                # 检查是否到了触发时间
                trigger = pattern.trigger_conditions or {}
                if self._should_trigger_pattern(trigger):
                    notifications.append(ProactiveNotification(
                        notification_type="suggestion",
                        title="习惯提醒",
                        content=f"💡 {pattern.pattern_name}",
                        priority=2,
                        action_data=pattern.expected_action
                    ))
        
        return notifications[:2]  # 最多2个推荐
    
    def _should_trigger_pattern(self, trigger: Dict) -> bool:
        """检查是否应该触发模式"""
        now = datetime.now()
        
        # 检查时间条件
        if "hour" in trigger:
            if now.hour != trigger["hour"]:
                return False
        
        if "weekday" in trigger:
            if now.weekday() != trigger["weekday"]:
                return False
        
        if "day_of_month" in trigger:
            if now.day != trigger["day_of_month"]:
                return False
        
        return True
    
    # ==================== 特定场景服务 ====================
    
    async def prepare_for_event(
        self, 
        user_id: str, 
        event_type: str, 
        event_details: Dict
    ) -> List[ProactiveNotification]:
        """为特定事件准备通知"""
        
        notifications = []
        
        if event_type == "travel":
            # 出差/旅行准备
            destination = event_details.get("destination", "")
            date = event_details.get("date", "")
            
            notifications.append(ProactiveNotification(
                notification_type="suggestion",
                title="出行准备清单",
                content=f"📍 {destination} 出行准备\n\n建议准备:\n• 检查天气预报\n• 预订交通\n• 预订住宿\n• 准备必需物品",
                priority=4,
                suggestions=["查看天气", "生成行李清单", "查看日程"]
            ))
        
        elif event_type == "meeting":
            # 会议准备
            title = event_details.get("title", "会议")
            
            notifications.append(ProactiveNotification(
                notification_type="suggestion",
                title="会议准备",
                content=f"📋 {title} 准备事项\n\n• 回顾上次会议纪要\n• 准备讨论要点\n• 确认参会人员",
                priority=4,
                suggestions=["查看上次纪要", "准备材料", "发送提醒"]
            ))
        
        elif event_type == "deadline":
            # 截止日期准备
            task_name = event_details.get("task", "任务")
            
            notifications.append(ProactiveNotification(
                notification_type="alert",
                title="截止日期临近",
                content=f"⏰ {task_name} 即将到期\n\n建议:\n• 检查完成进度\n• 分解剩余工作\n• 需要帮助请告诉我",
                priority=5,
                suggestions=["查看进度", "分解任务", "申请延期"]
            ))
        
        return notifications
    
    # ==================== 创建主动任务 ====================
    
    async def create_proactive_task(
        self,
        user_id: str,
        task_type: str,
        trigger_type: str,
        title: str,
        content: str = "",
        trigger_time: datetime = None,
        trigger_condition: Dict = None,
        is_recurring: bool = False,
        recurrence_rule: Dict = None
    ) -> ProactiveTask:
        """创建主动服务任务"""
        
        task = ProactiveTask(
            user_id=user_id,
            task_type=task_type,
            trigger_type=trigger_type,
            title=title,
            content=content,
            trigger_time=trigger_time,
            trigger_condition=trigger_condition or {},
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule or {}
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    async def get_pending_proactive_tasks(
        self, 
        user_id: str
    ) -> List[ProactiveTask]:
        """获取待触发的主动任务"""
        
        now = datetime.now()
        
        return self.db.query(ProactiveTask).filter(
            and_(
                ProactiveTask.user_id == user_id,
                ProactiveTask.status == "pending",
                or_(
                    ProactiveTask.trigger_time <= now,
                    ProactiveTask.trigger_type == "condition"
                )
            )
        ).all()
