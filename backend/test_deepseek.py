#!/usr/bin/env python3
"""
快速测试DeepSeek API
"""
import asyncio
from app.core.llm_factory import get_provider
from app.core.llm_config import LLMProviderType
from app.core.llm_provider import ChatRequest, Message


async def test_deepseek():
    """测试DeepSeek对话"""
    print("🚀 测试DeepSeek API...")
    print("=" * 50)
    
    try:
        # 获取Provider（会自动使用DeepSeek配置）
        provider = get_provider(LLMProviderType.OPENAI)
        
        print(f"✅ Provider配置:")
        print(f"   API Key: {provider.api_key[:20]}...")
        print(f"   Base URL: {provider.base_url}")
        print(f"   Model: {provider.default_model}")
        print()
        
        # 测试简单对话
        print("📝 测试1: 简单对话")
        request = ChatRequest(
            messages=[
                Message(role="user", content="用一句话介绍人工智能")
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        response = await provider.chat(request)
        print(f"✅ 响应: {response.content}")
        print(f"📊 Token使用: {response.usage}")
        print(f"💰 预估成本: ~${(response.usage['total_tokens'] / 1000) * 0.00021:.6f} USD")
        print()
        
        # 测试流式对话
        print("📝 测试2: 流式对话")
        print("✅ 响应: ", end="", flush=True)
        
        request2 = ChatRequest(
            messages=[
                Message(role="user", content="数到5")
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        async for chunk in provider.chat_stream(request2):
            print(chunk, end="", flush=True)
        print("\n")
        
        # 测试中文能力
        print("📝 测试3: 中文能力")
        request3 = ChatRequest(
            messages=[
                Message(role="user", content="写一首关于春天的五言绝句")
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        response3 = await provider.chat(request3)
        print(f"✅ 响应:\n{response3.content}")
        print(f"📊 Token使用: {response3.usage}")
        print()
        
        # 测试代码生成
        print("📝 测试4: 代码生成能力")
        request4 = ChatRequest(
            messages=[
                Message(role="user", content="用Python写一个快速排序函数")
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        response4 = await provider.chat(request4)
        print(f"✅ 响应:\n{response4.content}")
        print(f"📊 Token使用: {response4.usage}")
        print()
        
        print("=" * 50)
        print("🎉 DeepSeek API测试全部通过！")
        print()
        print("💡 性价比分析:")
        total_tokens = (
            response.usage['total_tokens'] +
            response3.usage['total_tokens'] +
            response4.usage['total_tokens']
        )
        deepseek_cost = (total_tokens / 1000) * 0.00021
        gpt35_cost = (total_tokens / 1000) * 0.001
        print(f"   总Token数: {total_tokens}")
        print(f"   DeepSeek成本: ${deepseek_cost:.6f} USD")
        print(f"   GPT-3.5成本: ${gpt35_cost:.6f} USD")
        print(f"   节省: {((gpt35_cost - deepseek_cost) / gpt35_cost * 100):.1f}%")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_deepseek())
