"""
Few-shot Examples库
为各Agent提供高质量的示例数据
"""
from typing import List, Dict


class FewShotExamples:
    """Few-shot示例集合"""
    
    # ========== Coordinator（主控Agent）示例 ==========
    COORDINATOR_EXAMPLES = [
        {
            "input": "明天下午3点提醒我开会",
            "output": {
                "task_type": "reminder",
                "assigned_agent": "ReminderAgent",
                "parameters": {
                    "content": "开会",
                    "time": "明天下午3点"
                },
                "confidence": 0.95
            }
        },
        {
            "input": "帮我写一个Python快速排序算法",
            "output": {
                "task_type": "code",
                "assigned_agent": "CodeAgent",
                "parameters": {
                    "language": "Python",
                    "algorithm": "快速排序",
                    "description": "实现快速排序算法"
                },
                "confidence": 0.92
            }
        },
        {
            "input": "本周五前完成项目报告",
            "output": {
                "task_type": "task",
                "assigned_agent": "TaskAgent",
                "parameters": {
                    "title": "完成项目报告",
                    "deadline": "本周五",
                    "priority": "high"
                },
                "confidence": 0.90
            }
        },
        {
            "input": "下周一早上9点和张三讨论项目",
            "output": {
                "task_type": "schedule",
                "assigned_agent": "ScheduleAgent",
                "parameters": {
                    "title": "与张三讨论项目",
                    "time": "下周一早上9点",
                    "participants": ["张三"]
                },
                "confidence": 0.92
            }
        },
        {
            "input": "总结一下这篇文章的要点",
            "output": {
                "task_type": "summary",
                "assigned_agent": "SummaryAgent",
                "parameters": {
                    "content_type": "文章",
                    "output_format": "要点"
                },
                "confidence": 0.88
            }
        },
        {
            "input": "推荐几部科幻电影",
            "output": {
                "task_type": "recommendation",
                "assigned_agent": "RecommendationAgent",
                "parameters": {
                    "category": "电影",
                    "genre": "科幻",
                    "count": "几部"
                },
                "confidence": 0.90
            }
        },
        {
            "input": "北京明天天气怎么样？",
            "output": {
                "task_type": "weather",
                "assigned_agent": "WeatherAgent",
                "parameters": {
                    "city": "北京",
                    "date": "明天"
                },
                "confidence": 0.95
            }
        }
    ]
    
    # ========== ScheduleAgent（日程管理）示例 ==========
    SCHEDULE_EXAMPLES = [
        {
            "input": "下周一上午10点和张三讨论项目进度",
            "output": {
                "title": "与张三讨论项目进度",
                "start_time": "2026-01-20 10:00",
                "end_time": "2026-01-20 11:00",
                "participants": ["张三"],
                "type": "meeting"
            }
        },
        {
            "input": "每周五下午开周会",
            "output": {
                "title": "周会",
                "repeat": "weekly",
                "day_of_week": "Friday",
                "start_time": "14:00",
                "duration": "1 hour"
            }
        }
    ]
    
    # ========== TaskAgent（待办管理）示例 ==========
    TASK_EXAMPLES = [
        {
            "input": "本周五前完成项目报告，这个很重要",
            "output": {
                "title": "完成项目报告",
                "deadline": "2026-01-17",
                "priority": "high",
                "tags": ["工作", "报告"]
            }
        },
        {
            "input": "学习Python，预计需要3个月时间",
            "output": {
                "title": "学习Python",
                "estimated_time": "3个月",
                "priority": "medium",
                "tags": ["学习", "编程"],
                "subtasks": [
                    "学习基础语法",
                    "完成练习项目",
                    "深入学习框架"
                ]
            }
        }
    ]
    
    # ========== CodeAgent（代码助手）示例 ==========
    CODE_EXAMPLES = [
        {
            "input": "用Python写一个函数，判断一个数是否为质数",
            "output": """```python
def is_prime(n: int) -> bool:
    \"\"\"
    判断一个数是否为质数
    
    Args:
        n: 待判断的整数
    
    Returns:
        True if n is prime, False otherwise
    \"\"\"
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # 只需检查到sqrt(n)
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    
    return True
```

解释: 
1. 小于2的数不是质数
2. 2是最小的质数
3. 偶数（除2外）不是质数
4. 只需检查到√n，优化性能
5. 步长为2，只检查奇数"""
        }
    ]
    
    # ========== TranslationAgent（翻译服务）示例 ==========
    TRANSLATION_EXAMPLES = [
        {
            "input": "把'人工智能正在改变世界'翻译成英文",
            "output": {
                "source_lang": "中文",
                "target_lang": "英文",
                "source_text": "人工智能正在改变世界",
                "translated_text": "Artificial Intelligence is changing the world",
                "explanation": "AI/Artificial Intelligence 是人工智能的标准译法"
            }
        }
    ]
    
    # ========== SummaryAgent（文本总结）示例 ==========
    SUMMARY_EXAMPLES = [
        {
            "input": """
深度学习是机器学习的一个分支，它基于人工神经网络进行学习。
深度学习的"深度"指的是网络中的层数，通常包含多个隐藏层。
通过这些层，模型可以学习数据的高级抽象特征。
深度学习在图像识别、自然语言处理、语音识别等领域取得了突破性进展。
""",
            "output": {
                "type": "摘要式",
                "summary": "深度学习是基于多层神经网络的机器学习方法，通过学习数据的抽象特征，在计算机视觉和NLP等领域取得重大突破。",
                "key_points": [
                    "深度学习属于机器学习分支",
                    "基于多层神经网络",
                    "可学习高级抽象特征",
                    "在多个AI领域有突破"
                ]
            }
        }
    ]
    
    # ========== DataAnalysisAgent（数据分析）示例 ==========
    DATA_ANALYSIS_EXAMPLES = [
        {
            "input": "销售数据: [100, 120, 95, 130, 140, 125]",
            "output": {
                "statistics": {
                    "mean": 118.33,
                    "median": 122.5,
                    "std_dev": 16.67,
                    "trend": "上升"
                },
                "insights": [
                    "平均销售额为118.33",
                    "数据波动较小（标准差16.67）",
                    "整体呈上升趋势",
                    "第5期达到峰值140"
                ],
                "recommendations": [
                    "继续当前策略",
                    "关注异常下降期（第3期）的原因"
                ]
            }
        }
    ]
    
    @classmethod
    def get_examples(cls, agent_name: str, limit: int = 3) -> List[Dict]:
        """
        获取指定Agent的示例
        
        Args:
            agent_name: Agent名称
            limit: 返回示例数量
        
        Returns:
            示例列表
        """
        examples_map = {
            "Coordinator": cls.COORDINATOR_EXAMPLES,
            "ScheduleAgent": cls.SCHEDULE_EXAMPLES,
            "TaskAgent": cls.TASK_EXAMPLES,
            "CodeAgent": cls.CODE_EXAMPLES,
            "TranslationAgent": cls.TRANSLATION_EXAMPLES,
            "SummaryAgent": cls.SUMMARY_EXAMPLES,
            "DataAnalysisAgent": cls.DATA_ANALYSIS_EXAMPLES,
        }
        
        examples = examples_map.get(agent_name, [])
        return examples[:limit]
    
    @classmethod
    def format_examples_for_prompt(cls, agent_name: str, limit: int = 3) -> str:
        """
        格式化示例用于Prompt
        
        Args:
            agent_name: Agent名称
            limit: 示例数量
        
        Returns:
            格式化的示例文本
        """
        examples = cls.get_examples(agent_name, limit)
        if not examples:
            return ""
        
        formatted = "\n\n## 参考示例\n\n"
        for i, example in enumerate(examples, 1):
            formatted += f"### 示例 {i}\n"
            formatted += f"**输入**: {example.get('input', 'N/A')}\n\n"
            
            if 'analysis' in example:
                formatted += f"**分析**: {example['analysis']}\n\n"
            
            output = example.get('output', {})
            if isinstance(output, dict):
                formatted += "**输出**:\n```json\n"
                import json
                formatted += json.dumps(output, ensure_ascii=False, indent=2)
                formatted += "\n```\n\n"
            else:
                formatted += f"**输出**:\n{output}\n\n"
        
        return formatted


# 通用Few-shot提示模板
FEW_SHOT_TEMPLATE = """
请参考以下示例来处理类似的任务:

{examples}

现在，请处理以下新任务:
{new_task}
"""


def create_few_shot_prompt(agent_name: str, new_task: str, num_examples: int = 2) -> str:
    """
    创建包含Few-shot示例的Prompt
    
    Args:
        agent_name: Agent名称
        new_task: 新任务描述
        num_examples: 使用的示例数量
    
    Returns:
        完整的Prompt
    """
    examples_text = FewShotExamples.format_examples_for_prompt(agent_name, num_examples)
    
    return FEW_SHOT_TEMPLATE.format(
        examples=examples_text,
        new_task=new_task
    )
