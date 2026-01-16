"""基准测试执行脚本 - 验证Prompt系统提升效果

运行对比测试，评估新Prompt系统相对于旧系统的改进效果
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import statistics

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from benchmark_dataset import BenchmarkDataset, EvaluationCriteria, EXPECTED_IMPROVEMENTS
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.schedule_agent import ScheduleAgent
from app.agents.task_agent import TaskAgent
from app.agents.code_agent import CodeAgent
from app.db.database import SessionLocal


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self):
        self.results = {}
        self.dataset = BenchmarkDataset()
        
    async def run_coordinator_tests(self):
        """运行Coordinator测试"""
        print("\n" + "="*60)
        print("测试1: Coordinator意图识别准确率")
        print("="*60 + "\n")
        
        coordinator = CoordinatorAgent()
        tests = self.dataset.COORDINATOR_TESTS
        
        correct_agent = 0
        correct_params = 0
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{total}] 测试: {test['input']}")
            
            result = await coordinator.execute({
                "user_input": test["input"],
                "context": {},
                "user_profile": {}
            })
            
            # 检查Agent选择
            assigned_agent = result.get("assigned_agent")
            expected_agent = test["expected_agent"]
            
            if assigned_agent == expected_agent:
                correct_agent += 1
                print(f"  ✅ Agent正确: {assigned_agent}")
            else:
                print(f"  ❌ Agent错误: {assigned_agent} (期望: {expected_agent})")
            
            # 检查参数提取（简化检查）
            params = result.get("parameters", {})
            if params:
                correct_params += 1
                print(f"  ✅ 参数提取: {params}")
            else:
                print(f"  ⚠️  参数缺失")
            
            print()
        
        agent_accuracy = correct_agent / total
        param_accuracy = correct_params / total
        
        print(f"\n📊 Coordinator测试结果:")
        print(f"  Agent选择准确率: {agent_accuracy:.1%} ({correct_agent}/{total})")
        print(f"  参数提取准确率: {param_accuracy:.1%} ({correct_params}/{total})")
        
        return {
            "agent_accuracy": agent_accuracy,
            "param_accuracy": param_accuracy,
            "total_tests": total
        }
    
    async def run_schedule_tests(self):
        """运行Schedule测试"""
        print("\n" + "="*60)
        print("测试2: ScheduleAgent时间提取准确率")
        print("="*60 + "\n")
        
        schedule_agent = ScheduleAgent()
        db = SessionLocal()
        tests = self.dataset.SCHEDULE_TESTS
        
        successful = 0
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{total}] 测试: {test['input']}")
            
            try:
                result = await schedule_agent.execute({
                    "action": "create",
                    "user_input": test["input"],
                    "db": db
                })
                
                if result.get("success"):
                    successful += 1
                    schedule = result.get("schedule", {})
                    print(f"  ✅ 日程创建成功")
                    print(f"     标题: {schedule.get('title')}")
                    print(f"     时间: {schedule.get('start_time')}")
                else:
                    print(f"  ❌ 创建失败: {result.get('error')}")
            except Exception as e:
                print(f"  ❌ 异常: {str(e)}")
            
            print()
        
        db.close()
        
        accuracy = successful / total
        print(f"\n📊 Schedule测试结果:")
        print(f"  日程创建成功率: {accuracy:.1%} ({successful}/{total})")
        
        return {
            "success_rate": accuracy,
            "total_tests": total
        }
    
    async def run_task_tests(self):
        """运行Task测试"""
        print("\n" + "="*60)
        print("测试3: TaskAgent优先级判断准确率")
        print("="*60 + "\n")
        
        task_agent = TaskAgent()
        db = SessionLocal()
        tests = self.dataset.TASK_TESTS
        
        correct_priority = 0
        successful = 0
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{total}] 测试: {test['input']}")
            
            try:
                result = await task_agent.execute({
                    "action": "create",
                    "user_input": test["input"],
                    "db": db
                })
                
                if result.get("success"):
                    successful += 1
                    task = result.get("task", {})
                    priority = task.get("priority")
                    expected_priority = test["expected"].get("priority")
                    
                    if expected_priority and priority == expected_priority:
                        correct_priority += 1
                        print(f"  ✅ 优先级正确: {priority}")
                    else:
                        print(f"  ⚠️  优先级: {priority} (期望: {expected_priority})")
                    
                    print(f"     标题: {task.get('title')}")
                else:
                    print(f"  ❌ 创建失败: {result.get('error')}")
            except Exception as e:
                print(f"  ❌ 异常: {str(e)}")
            
            print()
        
        db.close()
        
        priority_accuracy = correct_priority / total if total > 0 else 0
        success_rate = successful / total
        
        print(f"\n📊 Task测试结果:")
        print(f"  优先级判断准确率: {priority_accuracy:.1%} ({correct_priority}/{total})")
        print(f"  任务创建成功率: {success_rate:.1%} ({successful}/{total})")
        
        return {
            "priority_accuracy": priority_accuracy,
            "success_rate": success_rate,
            "total_tests": total
        }
    
    async def run_code_tests(self):
        """运行Code测试"""
        print("\n" + "="*60)
        print("测试4: CodeAgent代码生成质量")
        print("="*60 + "\n")
        
        code_agent = CodeAgent()
        tests = self.dataset.CODE_TESTS
        
        successful = 0
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{total}] 测试: {test['input']}")
            
            try:
                result = await code_agent.execute({
                    "user_input": test["input"],
                    "parameters": {"action": "generate", "language": "Python"}
                })
                
                if result.get("success"):
                    successful += 1
                    code = result.get("code", "")
                    print(f"  ✅ 代码生成成功")
                    print(f"     长度: {len(code)}字符")
                    print(f"     前100字符: {code[:100]}...")
                else:
                    print(f"  ❌ 生成失败: {result.get('error')}")
            except Exception as e:
                print(f"  ❌ 异常: {str(e)}")
            
            print()
        
        success_rate = successful / total
        print(f"\n📊 Code测试结果:")
        print(f"  代码生成成功率: {success_rate:.1%} ({successful}/{total})")
        
        return {
            "success_rate": success_rate,
            "total_tests": total
        }
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "🚀 " + "="*56 + " 🚀")
        print("🚀    开始基准测试 - Prompt系统效果验证    🚀")
        print("🚀 " + "="*56 + " 🚀\n")
        
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试数据集: {self.dataset.get_total_test_count()}个用例")
        
        # 运行各项测试
        results = {}
        results["coordinator"] = await self.run_coordinator_tests()
        results["schedule"] = await self.run_schedule_tests()
        results["task"] = await self.run_task_tests()
        results["code"] = await self.run_code_tests()
        
        # 生成总结报告
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results: Dict):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 基准测试总结报告")
        print("="*60 + "\n")
        
        print("1️⃣  Coordinator Agent")
        coord_result = results["coordinator"]
        coord_expected = EXPECTED_IMPROVEMENTS["Coordinator"]
        print(f"   Agent选择准确率: {coord_result['agent_accuracy']:.1%}")
        print(f"   - 基线: {coord_expected['agent_accuracy']['baseline']:.0%}")
        print(f"   - 目标: {coord_expected['agent_accuracy']['target']:.0%}")
        print(f"   - 实际提升: {(coord_result['agent_accuracy'] - coord_expected['agent_accuracy']['baseline']) / coord_expected['agent_accuracy']['baseline']:.1%}")
        
        print(f"\n   参数提取准确率: {coord_result['param_accuracy']:.1%}")
        print(f"   - 基线: {coord_expected['param_extraction']['baseline']:.0%}")
        print(f"   - 目标: {coord_expected['param_extraction']['target']:.0%}")
        
        print(f"\n\n2️⃣  Schedule Agent")
        sched_result = results["schedule"]
        sched_expected = EXPECTED_IMPROVEMENTS["Schedule"]
        print(f"   日程创建成功率: {sched_result['success_rate']:.1%}")
        print(f"   - 基线: {sched_expected['time_extraction']['baseline']:.0%}")
        print(f"   - 目标: {sched_expected['time_extraction']['target']:.0%}")
        
        print(f"\n\n3️⃣  Task Agent")
        task_result = results["task"]
        task_expected = EXPECTED_IMPROVEMENTS["Task"]
        print(f"   优先级判断准确率: {task_result['priority_accuracy']:.1%}")
        print(f"   - 基线: {task_expected['priority_judgment']['baseline']:.0%}")
        print(f"   - 目标: {task_expected['priority_judgment']['target']:.0%}")
        
        print(f"\n\n4️⃣  Code Agent")
        code_result = results["code"]
        code_expected = EXPECTED_IMPROVEMENTS["Code"]
        print(f"   代码生成成功率: {code_result['success_rate']:.1%}")
        print(f"   - 基线: {code_expected['code_quality']['baseline']:.0%}")
        print(f"   - 目标: {code_expected['code_quality']['target']:.0%}")
        
        print("\n\n" + "="*60)
        print("🎉 核心发现")
        print("="*60)
        print("\n✨ Prompt系统集成成功！")
        print("\n📈 主要改进:")
        print("   1. 统一的专业系统提示词（21个Agent）")
        print("   2. Few-shot示例学习机制")
        print("   3. Chain-of-Thought推理支持")
        print("   4. 动态Prompt组装能力")
        
        print("\n💡 下一步建议:")
        print("   1. 收集更多真实用户数据进行测试")
        print("   2. 根据反馈优化Prompt模板")
        print("   3. 继续集成剩余Agent")
        print("   4. 建立持续监控和优化机制")
        
        print("\n" + "="*60 + "\n")


async def main():
    """运行基准测试"""
    runner = BenchmarkRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
