"""
LLM Provider测试脚本
用于验证各个provider的基本功能
"""
import asyncio
import os
from app.core.llm_factory import get_provider
from app.core.llm_config import LLMProviderType
from app.core.llm_provider import ChatRequest, Message


async def test_openai():
    """测试OpenAI Provider"""
    print("=" * 50)
    print("测试 OpenAI Provider")
    print("=" * 50)
    
    # 检查API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY未设置，跳过测试")
        return
    
    try:
        provider = get_provider(LLMProviderType.OPENAI)
        
        # 测试非流式对话
        print("\n1. 测试非流式对话...")
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
        
        # 测试流式对话
        print("\n2. 测试流式对话...")
        print("✅ 响应: ", end="", flush=True)
        async for chunk in provider.chat_stream(request):
            print(chunk, end="", flush=True)
        print()
        
        # 测试token计数
        print("\n3. 测试token计数...")
        token_count = await provider.count_tokens("Hello, world!", "gpt-3.5-turbo")
        print(f"✅ Token数量: {token_count}")
        
        # 获取可用模型
        print("\n4. 获取可用模型...")
        models = provider.get_available_models()
        print(f"✅ 可用模型: {', '.join(models)}")
        
        print("\n✅ OpenAI Provider测试通过！\n")
        
    except Exception as e:
        print(f"\n❌ OpenAI Provider测试失败: {str(e)}\n")


async def test_anthropic():
    """测试Anthropic Provider"""
    print("=" * 50)
    print("测试 Anthropic Provider")
    print("=" * 50)
    
    # 检查API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY未设置，跳过测试")
        return
    
    try:
        provider = get_provider(LLMProviderType.ANTHROPIC)
        
        # 测试非流式对话
        print("\n1. 测试非流式对话...")
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
        
        # 测试流式对话
        print("\n2. 测试流式对话...")
        print("✅ 响应: ", end="", flush=True)
        async for chunk in provider.chat_stream(request):
            print(chunk, end="", flush=True)
        print()
        
        # 获取可用模型
        print("\n3. 获取可用模型...")
        models = provider.get_available_models()
        print(f"✅ 可用模型: {', '.join(models)}")
        
        print("\n✅ Anthropic Provider测试通过！\n")
        
    except Exception as e:
        print(f"\n❌ Anthropic Provider测试失败: {str(e)}\n")


async def test_ollama():
    """测试Ollama Provider"""
    print("=" * 50)
    print("测试 Ollama Provider")
    print("=" * 50)
    
    try:
        provider = get_provider(LLMProviderType.OLLAMA)
        
        # 测试非流式对话
        print("\n1. 测试非流式对话...")
        request = ChatRequest(
            messages=[
                Message(role="user", content="Say hello in one sentence")
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        response = await provider.chat(request)
        print(f"✅ 响应: {response.content}")
        print(f"📊 Token使用: {response.usage}")
        
        # 测试流式对话
        print("\n2. 测试流式对话...")
        print("✅ 响应: ", end="", flush=True)
        async for chunk in provider.chat_stream(request):
            print(chunk, end="", flush=True)
        print()
        
        # 获取可用模型
        print("\n3. 获取可用模型...")
        models = provider.get_available_models()
        print(f"✅ 可用模型: {', '.join(models)}")
        
        print("\n✅ Ollama Provider测试通过！\n")
        
    except Exception as e:
        print(f"\n❌ Ollama Provider测试失败: {str(e)}\n")
        print("💡 提示: 确保Ollama正在运行 (ollama serve)")


async def main():
    """主测试函数"""
    print("\n🚀 开始LLM Provider测试...\n")
    
    # 测试各个provider
    await test_openai()
    await test_anthropic()
    await test_ollama()
    
    print("=" * 50)
    print("🎉 所有测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
