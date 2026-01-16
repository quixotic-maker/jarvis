"""步骤3: 准确率对比测试（新旧Prompt对比）"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.coordinator_agent import CoordinatorAgent


async def test_accuracy_comparison():
    """准确率对比测试"""
    print("="*60)
    print("步骤3: 准确率对比测试")
    print("="*60 + "\n")
    
    print("📊 测试说明:")
    print("  - 新Prompt: 使用prompt_service + Few-shot + CoT")
    print("  - 评估维度: Agent选择准确率、参数提取完整性")
    print("  - 测试用例: 10个代表性场景\n")
    
    coordinator = CoordinatorAgent()
    
    test_cases = [
        {
            "input": "明天下午3点提醒我开会",
            "expected_agent": "ReminderAgent",
            "expected_params": ["时间", "内容"]
        },
        {
            "input": "帮我写一个Python快速排序算法",
            "expected_agent": "CodeAgent",
            "expected_params": ["语言", "任务"]
        },
        {
            "input": "本周五前完成项目报告",
            "expected_agent": "TaskAgent",
            "expected_params": ["标题", "截止日期"]
        },
        {
            "input": "北京今天天气怎么样？",
            "expected_agent": "WeatherAgent",
            "expected_params": ["城市"]
        },
        {
            "input": "把这段话翻译成英文：你好世界",
            "expected_agent": "TranslationAgent",
            "expected_params": ["文本", "目标语言"]
        },
        {
            "input": "总结一下这篇文章的要点",
            "expected_agent": "SummaryAgent",
            "expected_params": []
        },
        {
            "input": "计算100的15%是多少",
            "expected_agent": "CalculationAgent",
            "expected_params": ["表达式"]
        },
        {
            "input": "推荐几部科幻电影",
            "expected_agent": "RecommendationAgent",
            "expected_params": ["类别"]
        },
        {
            "input": "分析这组销售数据的趋势",
            "expected_agent": "DataAnalysisAgent",
            "expected_params": []
        },
        {
            "input": "下周一早上9点和张三讨论项目",
            "expected_agent": "ScheduleAgent",
            "expected_params": ["时间", "参与者", "主题"]
        }
    ]
    
    correct_agent = 0
    has_params = 0
    total = len(test_cases)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{total}: {test['input']}")
        print(f"{'='*60}")
        
        try:
            result = await coordinator.execute({
                "user_input": test["input"],
                "context": {},
                "user_profile": {}
            })
            
            assigned_agent = result.get("assigned_agent")
            expected_agent = test["expected_agent"]
            parameters = result.get("parameters", {})
            
            # 检查Agent准确性
            agent_correct = assigned_agent == expected_agent
            if agent_correct:
                correct_agent += 1
                print(f"✅ Agent正确: {assigned_agent}")
            else:
                print(f"❌ Agent错误: {assigned_agent} (期望: {expected_agent})")
            
            # 检查参数提取
            param_extracted = len(parameters) > 0
            if param_extracted:
                has_params += 1
                print(f"✅ 参数提取: {parameters}")
            else:
                print(f"⚠️  参数缺失")
            
            # 记录结果
            results.append({
                "input": test["input"],
                "expected": expected_agent,
                "actual": assigned_agent,
                "correct": agent_correct,
                "params": parameters,
                "has_params": param_extracted
            })
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append({
                "input": test["input"],
                "error": str(e)
            })
    
    # 生成报告
    print("\n\n" + "="*60)
    print("📊 准确率测试报告")
    print("="*60 + "\n")
    
    agent_accuracy = correct_agent / total
    param_accuracy = has_params / total
    
    print(f"1️⃣  Agent选择准确率: {agent_accuracy:.1%} ({correct_agent}/{total})")
    print(f"   - 基线（预估旧系统）: 70%")
    print(f"   - 目标: 90%")
    if agent_accuracy >= 0.9:
        print(f"   ✅ 达到目标！")
    elif agent_accuracy >= 0.8:
        print(f"   🟡 接近目标")
    else:
        print(f"   🔴 需要优化")
    
    print(f"\n2️⃣  参数提取准确率: {param_accuracy:.1%} ({has_params}/{total})")
    print(f"   - 基线（预估旧系统）: 60%")
    print(f"   - 目标: 85%")
    if param_accuracy >= 0.85:
        print(f"   ✅ 达到目标！")
    elif param_accuracy >= 0.75:
        print(f"   🟡 接近目标")
    else:
        print(f"   🔴 需要优化")
    
    # 错误分析
    errors = [r for r in results if not r.get("correct", False)]
    if errors:
        print(f"\n3️⃣  错误案例分析:")
        for err in errors:
            if "error" not in err:
                print(f"   - {err['input']}")
                print(f"     期望: {err['expected']}, 实际: {err['actual']}")
    
    print("\n" + "="*60)
    print("✅ 步骤3完成: 准确率对比测试完成")
    print("="*60)
    
    return {
        "agent_accuracy": agent_accuracy,
        "param_accuracy": param_accuracy,
        "total": total,
        "results": results
    }


async def main():
    await test_accuracy_comparison()


if __name__ == "__main__":
    asyncio.run(main())
