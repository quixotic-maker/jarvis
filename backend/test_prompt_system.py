#!/usr/bin/env python3
"""
测试Prompt系统
验证各个Agent的Prompt生成效果
"""
import asyncio
from app.core.prompt_service import prompt_service, get_agent_prompt, get_agent_messages
from app.core.cot_prompts import CoTPattern
from app.core.llm_factory import get_provider
from app.core.llm_config import LLMProviderType
from app.core.llm_provider import ChatRequest, Message


async def test_basic_prompts():
    """测试基础Prompt生成"""
    print("=" * 60)
    print("测试1: 基础Prompt生成")
    print("=" * 60)
    
    agents = ["Coordinator", "ScheduleAgent", "TaskAgent", "CodeAgent"]
    
    for agent_name in agents:
        prompt = get_agent_prompt(
            agent_name,
            "这是一个测试输入"
        )
        print(f"\n### {agent_name} Prompt (前200字符):")
        print(prompt[:200] + "...")
        print()


async def test_few_shot_prompts():
    """测试Few-shot Prompt"""
    print("=" * 60)
    print("测试2: Few-shot Prompt生成")
    print("=" * 60)
    
    prompt = get_agent_prompt(
        "ScheduleAgent",
        "下周三下午2点和李四开会讨论新产品",
        use_few_shot=True,
        num_examples=2
    )
    
    print("\n### ScheduleAgent Few-shot Prompt (前400字符):")
    print(prompt[:400] + "...")
    print()


async def test_cot_prompts():
    """测试Chain-of-Thought Prompt"""
    print("=" * 60)
    print("测试3: Chain-of-Thought Prompt生成")
    print("=" * 60)
    
    prompt = get_agent_prompt(
        "CalculationAgent",
        "一个商品原价200元，先打8折，再满300减50，买2件最终多少钱？",
        use_cot=True,
        cot_pattern=CoTPattern.STEP_BY_STEP
    )
    
    print("\n### CalculationAgent CoT Prompt (前500字符):")
    print(prompt[:500] + "...")
    print()


async def test_combined_prompts():
    """测试组合Prompt（Few-shot + CoT）"""
    print("=" * 60)
    print("测试4: 组合Prompt (Few-shot + CoT)")
    print("=" * 60)
    
    prompt = get_agent_prompt(
        "CodeAgent",
        "用Python实现二分查找算法",
        use_few_shot=True,
        use_cot=True,
        cot_pattern=CoTPattern.STEP_BY_STEP,
        constraints=[
            "代码需要有详细注释",
            "包含测试用例",
            "时间复杂度O(log n)"
        ],
        output_format="```python\n代码\n```\n\n解释: ..."
    )
    
    print("\n### CodeAgent 组合Prompt (前600字符):")
    print(prompt[:600] + "...")
    print()


async def test_messages_format():
    """测试消息格式（Chat API）"""
    print("=" * 60)
    print("测试5: 消息格式生成")
    print("=" * 60)
    
    messages = get_agent_messages(
        "TaskAgent",
        "帮我规划一下本周的学习任务",
        use_few_shot=True,
        num_examples=1
    )
    
    print(f"\n### TaskAgent 消息列表 ({len(messages)}条消息):")
    for i, msg in enumerate(messages, 1):
        print(f"\n消息 {i} ({msg['role']}):")
        content = msg['content']
        if len(content) > 200:
            print(content[:200] + "...")
        else:
            print(content)
    print()


async def test_real_llm_call():
    """测试真实LLM调用"""
    print("=" * 60)
    print("测试6: 真实LLM调用测试")
    print("=" * 60)
    
    try:
        # 获取Provider
        provider = get_provider(LLMProviderType.OPENAI)
        
        # 生成Prompt
        messages = get_agent_messages(
            "InfoRetrievalAgent",
            "什么是人工智能？请用一句话解释",
            use_few_shot=False,
            constraints=["回答要简洁", "不超过50字"]
        )
        
        # 转换为ChatRequest格式
        request_messages = [
            Message(role=msg['role'], content=msg['content'])
            for msg in messages
        ]
        
        request = ChatRequest(
            messages=request_messages,
            temperature=0.7,
            max_tokens=100
        )
        
        print("\n### 发送请求到LLM...")
        response = await provider.chat(request)
        
        print(f"\n✅ LLM响应:")
        print(response.content)
        print(f"\n📊 Token使用: {response.usage}")
        
    except Exception as e:
        print(f"\n❌ LLM调用失败: {str(e)}")
        print("提示: 请确保配置了有效的API密钥")


async def test_prompt_statistics():
    """测试Prompt统计信息"""
    print("\n" + "=" * 60)
    print("Prompt系统统计")
    print("=" * 60)
    
    templates = prompt_service.library.list_templates()
    print(f"\n✅ 已注册的Prompt模板: {len(templates)}个")
    print("\n模板列表:")
    for i, name in enumerate(templates, 1):
        template = prompt_service.library.get(name)
        print(f"  {i}. {name} (v{template.version})")
    
    print(f"\n✅ 支持的CoT模式: {len(CoTPattern.__members__)}种")
    print("CoT模式列表:")
    for i, pattern in enumerate(CoTPattern, 1):
        print(f"  {i}. {pattern.value}")
    
    print("\n" + "=" * 60)


async def main():
    """主测试函数"""
    print("\n🚀 开始测试Prompt系统...\n")
    
    # 运行所有测试
    await test_basic_prompts()
    await test_few_shot_prompts()
    await test_cot_prompts()
    await test_combined_prompts()
    await test_messages_format()
    await test_real_llm_call()
    await test_prompt_statistics()
    
    print("\n🎉 所有测试完成！")
    print("\n💡 Prompt系统特性:")
    print("  ✅ 21个Agent专业Prompt")
    print("  ✅ Few-shot示例支持")
    print("  ✅ 5种Chain-of-Thought模式")
    print("  ✅ 灵活的Prompt组装")
    print("  ✅ Chat API格式支持")
    print()


if __name__ == "__main__":
    asyncio.run(main())
