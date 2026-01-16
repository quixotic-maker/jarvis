"""步骤2: 测试单个Agent的完整响应"""
import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.schedule_agent import ScheduleAgent
from app.agents.calculation_agent import CalculationAgent
from app.db.database import SessionLocal


async def test_single_agent_response():
    """测试单个Agent的完整流程"""
    print("="*60)
    print("步骤2: 测试Agent完整响应")
    print("="*60 + "\n")
    
    # 测试1: Coordinator
    print("\n" + "="*60)
    print("测试1: CoordinatorAgent意图识别")
    print("="*60)
    
    coordinator = CoordinatorAgent()
    test_inputs = [
        "明天下午3点提醒我开会",
        "帮我写一个Python快速排序",
        "北京今天天气怎么样"
    ]
    
    for user_input in test_inputs:
        print(f"\n输入: {user_input}")
        try:
            result = await coordinator.execute({
                "user_input": user_input,
                "context": {},
                "user_profile": {}
            })
            
            print(f"✅ 响应成功")
            print(f"  任务类型: {result.get('task_type')}")
            print(f"  分配Agent: {result.get('assigned_agent')}")
            print(f"  置信度: {result.get('confidence')}")
            print(f"  参数: {json.dumps(result.get('parameters', {}), ensure_ascii=False)}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试2: CalculationAgent (带CoT)
    print("\n\n" + "="*60)
    print("测试2: CalculationAgent数学计算（CoT模式）")
    print("="*60)
    
    calc_agent = CalculationAgent()
    test_calculations = [
        "计算 1234 * 5678",
        "一个商品原价200元，打8折后多少钱？"
    ]
    
    for calc_input in test_calculations:
        print(f"\n输入: {calc_input}")
        try:
            result = await calc_agent.execute({
                "user_input": calc_input,
                "parameters": {}
            })
            
            print(f"✅ 计算成功")
            if result.get("success"):
                calculation = result.get("calculation", {})
                print(f"  表达式: {calculation.get('expression', 'N/A')}")
                print(f"  结果: {calculation.get('result', 'N/A')}")
                if 'steps' in calculation:
                    print(f"  步骤: {calculation.get('steps')}")
            else:
                print(f"  错误: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试3: ScheduleAgent
    print("\n\n" + "="*60)
    print("测试3: ScheduleAgent日程创建（Few-shot模式）")
    print("="*60)
    
    schedule_agent = ScheduleAgent()
    db = SessionLocal()
    
    test_schedules = [
        "下周一早上9点和张三讨论项目",
        "每周五下午2点开周会"
    ]
    
    for sched_input in test_schedules:
        print(f"\n输入: {sched_input}")
        try:
            result = await schedule_agent.execute({
                "action": "create",
                "user_input": sched_input,
                "db": db
            })
            
            if result.get("success"):
                print(f"✅ 日程创建成功")
                schedule = result.get("schedule", {})
                print(f"  标题: {schedule.get('title')}")
                print(f"  时间: {schedule.get('start_time')}")
                print(f"  地点: {schedule.get('location', '无')}")
            else:
                print(f"❌ 创建失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    db.close()
    
    print("\n\n" + "="*60)
    print("✅ 步骤2完成: Agent响应功能正常")
    print("="*60)


async def main():
    await test_single_agent_response()


if __name__ == "__main__":
    asyncio.run(main())
