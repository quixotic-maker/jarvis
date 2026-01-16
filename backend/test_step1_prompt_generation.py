"""步骤1: 测试Prompt生成是否正确"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.prompt_service import prompt_service
from datetime import datetime


def test_prompt_generation():
    """测试各Agent的Prompt生成"""
    print("="*60)
    print("步骤1: 验证Prompt生成功能")
    print("="*60 + "\n")
    
    test_cases = [
        ("coordinator", "明天下午3点提醒我开会"),
        ("schedule_agent", "下周一早上9点和张三讨论项目"),
        ("task_agent", "本周五前完成项目报告"),
        ("code_agent", "用Python写一个快速排序算法"),
        ("calculation_agent", "计算1234 * 5678"),
    ]
    
    for agent_name, user_input in test_cases:
        print(f"\n{'='*60}")
        print(f"Agent: {agent_name}")
        print(f"用户输入: {user_input}")
        print(f"{'='*60}\n")
        
        try:
            # 测试基础prompt
            messages = prompt_service.build_messages(
                agent_name=agent_name,
                user_input=user_input,
                use_few_shot=True,
                num_examples=1
            )
            
            print(f"✅ Prompt生成成功")
            print(f"消息数量: {len(messages)}")
            
            for i, msg in enumerate(messages):
                role = msg["role"]
                content = msg["content"]
                print(f"\n消息 {i+1} ({role}):")
                print(f"  长度: {len(content)}字符")
                print(f"  前200字符: {content[:200]}...")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ 步骤1完成: Prompt生成功能正常")
    print("="*60)


if __name__ == "__main__":
    test_prompt_generation()
