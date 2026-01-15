#!/usr/bin/env python3
"""
创建测试数据脚本
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v2"

def create_schedule(title, description, start_offset_days, duration_hours, event_type="meeting", priority="medium"):
    """创建日程"""
    start_time = datetime.now() + timedelta(days=start_offset_days)
    end_time = start_time + timedelta(hours=duration_hours)
    
    data = {
        "title": title,
        "description": description,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "location": "会议室A",
        "attendees": ["张三", "李四"],
        "priority": priority,
        "event_type": event_type
    }
    
    response = requests.post(f"{BASE_URL}/schedules/", json=data)
    return response.json()

def create_task(title, description, priority="medium", tags=None):
    """创建任务"""
    due_date = datetime.now() + timedelta(days=3)
    
    data = {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_date.isoformat(),
        "tags": tags or ["测试"]
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=data)
    return response.json()

def main():
    print("🚀 开始创建测试数据...\n")
    
    # 创建日程
    print("📅 创建日程...")
    schedules = [
        create_schedule("产品评审会", "Q1产品路线图讨论", 1, 2, "meeting", "high"),
        create_schedule("技术分享", "React最佳实践", 2, 1, "meeting", "medium"),
        create_schedule("客户拜访", "大客户需求调研", 3, 3, "event", "high"),
        create_schedule("代码Review", "后端API代码审查", 0, 1, "task", "medium"),
        create_schedule("Sprint规划", "下周冲刺计划", 4, 2, "meeting", "high"),
    ]
    print(f"  ✅ 创建了 {len(schedules)} 个日程\n")
    
    # 创建任务
    print("✅ 创建任务...")
    tasks = [
        create_task("完成用户认证模块", "实现JWT登录和权限验证", "high", ["开发", "后端"]),
        create_task("优化数据库查询", "解决N+1查询问题", "high", ["性能", "数据库"]),
        create_task("编写API文档", "补充所有接口文档", "medium", ["文档"]),
        create_task("修复前端布局bug", "移动端适配问题", "medium", ["前端", "bug"]),
        create_task("准备演示PPT", "向客户展示新功能", "low", ["演示"]),
    ]
    print(f"  ✅ 创建了 {len(tasks)} 个任务\n")
    
    print("✨ 测试数据创建完成！")
    print(f"\n📊 统计:")
    print(f"  - 日程: {len(schedules)} 个")
    print(f"  - 任务: {len(tasks)} 个")

if __name__ == "__main__":
    main()
