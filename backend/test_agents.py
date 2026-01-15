"""Agent功能测试脚本"""
import asyncio
from app.agents import AGENT_REGISTRY


async def test_agents():
    """测试所有Agent"""
    print("=" * 60)
    print("Jarvis Agent 功能测试")
    print("=" * 60)
    print()
    
    # 测试用例
    test_cases = [
        {
            "agent": "ScheduleAgent",
            "input": {"user_input": "明天下午3点开会讨论项目", "action": "create"},
            "description": "日程管理测试"
        },
        {
            "agent": "EmailAgent",
            "input": {"user_input": "给张三写一封关于项目进展的邮件", "action": "compose"},
            "description": "邮件撰写测试"
        },
        {
            "agent": "WeatherAgent",
            "input": {"user_input": "查询北京的天气"},
            "description": "天气查询测试"
        },
        {
            "agent": "NewsAgent",
            "input": {"user_input": "获取今天的科技新闻"},
            "description": "新闻获取测试"
        },
        {
            "agent": "CalculationAgent",
            "input": {"user_input": "计算 123 * 456 + 789"},
            "description": "计算功能测试"
        },
        {
            "agent": "TranslationAgent",
            "input": {
                "user_input": "Hello, how are you?",
                "parameters": {"target_lang": "中文"}
            },
            "description": "翻译功能测试"
        },
        {
            "agent": "SummaryAgent",
            "input": {
                "user_input": "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。",
                "parameters": {"length": "short"}
            },
            "description": "文本总结测试"
        },
        {
            "agent": "FileAgent",
            "input": {"user_input": "搜索所有PDF文件", "action": "search"},
            "description": "文件搜索测试"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['description']}")
        print(f"   Agent: {test['agent']}")
        
        agent_class = AGENT_REGISTRY.get(test['agent'])
        if not agent_class:
            print(f"   ❌ Agent不存在\n")
            continue
        
        agent = agent_class()
        try:
            result = await agent.execute(test['input'])
            if result.get('success'):
                print(f"   ✅ 执行成功")
                # 打印部分结果
                if 'message' in result:
                    print(f"   📝 {result['message']}")
            else:
                print(f"   ❌ 执行失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
        
        print()
    
    print("=" * 60)
    print(f"测试完成！共测试 {len(test_cases)} 个Agent")
    print("=" * 60)


if __name__ == "__main__":
    # 注意：这个测试需要配置LLM API密钥才能运行
    print("⚠️  注意：请确保已在backend/.env中配置LLM API密钥")
    print()
    
    import sys
    sys.path.insert(0, "/home/liu/program/jarvis/backend")
    
    try:
        asyncio.run(test_agents())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n测试出错: {str(e)}")
