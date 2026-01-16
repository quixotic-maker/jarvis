"""步骤4: 性能基准测试（响应时间、Token使用）"""
import asyncio
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.code_agent import CodeAgent
from app.agents.calculation_agent import CalculationAgent


async def test_performance_benchmark():
    """性能基准测试"""
    print("="*60)
    print("步骤4: 性能基准测试")
    print("="*60 + "\n")
    
    print("📊 测试维度:")
    print("  - 响应时间")
    print("  - Token使用量（估算）")
    print("  - 输出质量\n")
    
    # 测试1: 简单任务响应时间
    print("\n" + "="*60)
    print("测试1: 简单任务响应时间（Coordinator）")
    print("="*60)
    
    coordinator = CoordinatorAgent()
    simple_tests = [
        "明天下午3点提醒我开会",
        "北京今天天气怎么样",
        "计算100+200"
    ]
    
    response_times = []
    
    for test_input in simple_tests:
        print(f"\n输入: {test_input}")
        start_time = time.time()
        
        try:
            result = await coordinator.execute({
                "user_input": test_input,
                "context": {},
                "user_profile": {}
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"✅ 响应时间: {response_time:.2f}秒")
            print(f"  分配Agent: {result.get('assigned_agent')}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"\n平均响应时间: {avg_time:.2f}秒")
        print(f"最快: {min(response_times):.2f}秒")
        print(f"最慢: {max(response_times):.2f}秒")
    
    # 测试2: 复杂任务响应时间（带CoT）
    print("\n\n" + "="*60)
    print("测试2: 复杂任务响应时间（CodeAgent with CoT）")
    print("="*60)
    
    code_agent = CodeAgent()
    complex_tests = [
        "用Python写一个快速排序算法",
        "实现二分查找算法"
    ]
    
    complex_times = []
    
    for test_input in complex_tests:
        print(f"\n输入: {test_input}")
        start_time = time.time()
        
        try:
            result = await code_agent.execute({
                "user_input": test_input,
                "parameters": {"action": "generate", "language": "Python"}
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            complex_times.append(response_time)
            
            if result.get("success"):
                code_length = len(result.get("code", ""))
                print(f"✅ 响应时间: {response_time:.2f}秒")
                print(f"  代码长度: {code_length}字符")
            else:
                print(f"❌ 失败: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    if complex_times:
        avg_time = sum(complex_times) / len(complex_times)
        print(f"\n平均响应时间: {avg_time:.2f}秒")
        print(f"最快: {min(complex_times):.2f}秒")
        print(f"最慢: {max(complex_times):.2f}秒")
    
    # 测试3: Token使用估算
    print("\n\n" + "="*60)
    print("测试3: Prompt长度估算（Token使用）")
    print("="*60)
    
    from app.core.prompt_service import prompt_service
    
    test_prompts = [
        ("coordinator", "明天下午3点提醒我开会", False, False),
        ("schedule_agent", "下周一早上9点开会", True, False),
        ("code_agent", "写一个快速排序", True, True),
        ("calculation_agent", "计算1234*5678", True, True),
    ]
    
    for agent_name, user_input, use_few_shot, use_cot in test_prompts:
        messages = prompt_service.build_messages(
            agent_name=agent_name,
            user_input=user_input,
            use_few_shot=use_few_shot,
            use_cot=use_cot
        )
        
        total_chars = sum(len(msg["content"]) for msg in messages)
        estimated_tokens = total_chars // 4  # 粗略估算：4字符≈1 token
        
        print(f"\n{agent_name}:")
        print(f"  Few-shot: {use_few_shot}, CoT: {use_cot}")
        print(f"  消息数: {len(messages)}")
        print(f"  总字符: {total_chars}")
        print(f"  估算Token: ~{estimated_tokens}")
    
    print("\n\n" + "="*60)
    print("📊 性能总结")
    print("="*60)
    
    if response_times and complex_times:
        print(f"\n简单任务平均响应: {sum(response_times)/len(response_times):.2f}秒")
        print(f"复杂任务平均响应: {sum(complex_times)/len(complex_times):.2f}秒")
        print(f"\n评估:")
        avg_simple = sum(response_times)/len(response_times)
        if avg_simple < 3:
            print(f"  ✅ 简单任务响应快速 (<3秒)")
        else:
            print(f"  ⚠️  简单任务响应较慢 (>{avg_simple:.1f}秒)")
    
    print("\n" + "="*60)
    print("✅ 步骤4完成: 性能基准测试完成")
    print("="*60)


async def main():
    await test_performance_benchmark()


if __name__ == "__main__":
    asyncio.run(main())
