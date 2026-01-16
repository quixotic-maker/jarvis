"""基准测试数据集 - 用于验证Prompt系统提升效果

这个数据集包含21个Agent的测试用例，用于对比新旧Prompt系统的效果
"""
from typing import Dict, List, Any


class BenchmarkDataset:
    """基准测试数据集"""
    
    # Coordinator - 意图识别测试（10个用例）
    COORDINATOR_TESTS = [
        {
            "input": "明天下午3点提醒我开会",
            "expected_agent": "ReminderAgent",
            "expected_params": {"time": "明天15:00", "content": "开会"}
        },
        {
            "input": "帮我写一个Python快速排序算法",
            "expected_agent": "CodeAgent",
            "expected_params": {"language": "Python", "task": "快速排序"}
        },
        {
            "input": "本周五前完成项目报告",
            "expected_agent": "TaskAgent",
            "expected_params": {"title": "完成项目报告", "deadline": "本周五", "priority": "high"}
        },
        {
            "input": "北京今天天气怎么样？",
            "expected_agent": "WeatherAgent",
            "expected_params": {"city": "北京", "time": "今天"}
        },
        {
            "input": "把这段话翻译成英文：你好世界",
            "expected_agent": "TranslationAgent",
            "expected_params": {"text": "你好世界", "target_lang": "英文"}
        },
        {
            "input": "总结一下这篇文章的要点",
            "expected_agent": "SummaryAgent",
            "expected_params": {}
        },
        {
            "input": "计算100的15%是多少",
            "expected_agent": "CalculationAgent",
            "expected_params": {"expression": "100 * 0.15"}
        },
        {
            "input": "推荐几部科幻电影",
            "expected_agent": "RecommendationAgent",
            "expected_params": {"category": "电影", "genre": "科幻"}
        },
        {
            "input": "分析这组销售数据的趋势",
            "expected_agent": "DataAnalysisAgent",
            "expected_params": {}
        },
        {
            "input": "下周一早上9点和张三讨论项目",
            "expected_agent": "ScheduleAgent",
            "expected_params": {"title": "与张三讨论项目", "time": "下周一09:00", "participants": ["张三"]}
        }
    ]
    
    # Schedule - 日程提取测试（5个用例）
    SCHEDULE_TESTS = [
        {
            "input": "下周三下午2点和李四开会讨论新产品",
            "expected": {
                "title": "与李四讨论新产品",
                "participants": ["李四"],
                "type": "meeting"
            }
        },
        {
            "input": "每周五下午开周会",
            "expected": {
                "title": "周会",
                "repeat": "weekly",
                "day_of_week": "Friday"
            }
        },
        {
            "input": "明天上午10点面试候选人",
            "expected": {
                "title": "面试候选人",
                "type": "interview"
            }
        },
        {
            "input": "本月25号晚上7点生日派对",
            "expected": {
                "title": "生日派对",
                "type": "personal"
            }
        },
        {
            "input": "下个月1号全天团建活动",
            "expected": {
                "title": "团建活动",
                "duration": "全天"
            }
        }
    ]
    
    # Task - 任务创建测试（5个用例）
    TASK_TESTS = [
        {
            "input": "本周五前完成项目报告，这个很重要",
            "expected": {
                "title": "完成项目报告",
                "priority": "high",
                "deadline_relative": "本周五"
            }
        },
        {
            "input": "学习Python基础知识，不着急",
            "expected": {
                "title": "学习Python基础知识",
                "priority": "low"
            }
        },
        {
            "input": "明天记得买生日礼物",
            "expected": {
                "title": "买生日礼物",
                "deadline_relative": "明天"
            }
        },
        {
            "input": "整理文档并发送给团队成员，今天完成",
            "expected": {
                "title": "整理文档并发送给团队",
                "deadline_relative": "今天",
                "priority": "high"
            }
        },
        {
            "input": "制定Q2营销计划",
            "expected": {
                "title": "制定Q2营销计划",
                "tags": ["工作", "计划"]
            }
        }
    ]
    
    # Code - 代码生成测试（5个用例）
    CODE_TESTS = [
        {
            "input": "用Python写一个判断质数的函数",
            "expected_features": ["函数定义", "参数检查", "算法实现", "注释"]
        },
        {
            "input": "实现二分查找算法",
            "expected_features": ["时间复杂度O(log n)", "边界处理", "测试用例"]
        },
        {
            "input": "写一个快速排序算法",
            "expected_features": ["递归实现", "分区函数", "性能分析"]
        },
        {
            "input": "生成斐波那契数列的前n项",
            "expected_features": ["迭代或递归", "性能优化", "边界处理"]
        },
        {
            "input": "实现一个简单的LRU缓存",
            "expected_features": ["数据结构选择", "get/put方法", "容量限制"]
        }
    ]
    
    # Translation - 翻译测试（5个用例）
    TRANSLATION_TESTS = [
        {
            "input": "把'Hello World'翻译成中文",
            "expected": {"source_lang": "英文", "target_lang": "中文", "text": "Hello World"}
        },
        {
            "input": "Translate this to English: 人工智能正在改变世界",
            "expected": {"source_lang": "中文", "target_lang": "英文"}
        },
        {
            "input": "将'机器学习'翻译成日语",
            "expected": {"source_lang": "中文", "target_lang": "日语", "text": "机器学习"}
        },
        {
            "input": "这句话用法语怎么说：我爱你",
            "expected": {"source_lang": "中文", "target_lang": "法语", "text": "我爱你"}
        },
        {
            "input": "翻译：Thank you for your help",
            "expected": {"source_lang": "英文", "target_lang": "中文"}
        }
    ]
    
    # Summary - 总结测试（3个用例）
    SUMMARY_TESTS = [
        {
            "input": """深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的表示。
            深度学习已经在图像识别、语音识别、自然语言处理等领域取得了突破性进展。
            卷积神经网络（CNN）适合处理图像数据，循环神经网络（RNN）适合处理序列数据，
            而Transformer架构则在自然语言处理任务中表现出色。""",
            "expected_features": ["关键概念提取", "结构清晰", "要点完整"]
        },
        {
            "input": """Python是一门解释型、面向对象的编程语言。它具有语法简洁、易于学习的特点。
            Python有丰富的标准库和第三方库，被广泛应用于Web开发、数据分析、人工智能等领域。""",
            "expected_features": ["简洁摘要", "关键特点", "应用领域"]
        },
        {
            "input": """敏捷开发是一种迭代式的软件开发方法。它强调快速交付、持续改进和团队协作。
            Scrum是最流行的敏捷框架之一，包括Sprint、每日站会、回顾会议等实践。""",
            "expected_features": ["核心理念", "关键实践", "框架介绍"]
        }
    ]
    
    # Calculation - 计算测试（5个用例）
    CALCULATION_TESTS = [
        {
            "input": "计算1234 * 5678",
            "expected": {"expression": "1234 * 5678", "result": 7006652}
        },
        {
            "input": "一个商品原价200元，先打8折，再满300减50，买2件最终多少钱？",
            "expected_features": ["步骤分解", "中间结果", "最终答案"]
        },
        {
            "input": "求解方程 2x + 3 = 7",
            "expected": {"result": 2, "steps": True}
        },
        {
            "input": "计算圆的面积，半径是5",
            "expected_features": ["公式", "计算过程", "结果"]
        },
        {
            "input": "100美元等于多少人民币？（汇率7.2）",
            "expected": {"result": 720, "unit": "人民币"}
        }
    ]
    
    # DataAnalysis - 数据分析测试（3个用例）
    DATA_ANALYSIS_TESTS = [
        {
            "input": "Q4销售额下降15%，请分析原因",
            "expected_features": ["问题识别", "可能原因", "数据需求", "建议"]
        },
        {
            "input": "用户增长率从20%降至5%，如何改善？",
            "expected_features": ["趋势分析", "影响因素", "改进策略"]
        },
        {
            "input": "分析以下销售数据：Q1: 100万, Q2: 120万, Q3: 150万, Q4: 140万",
            "expected_features": ["趋势描述", "增长率", "洞察发现"]
        }
    ]
    
    @classmethod
    def get_all_tests(cls) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有测试数据"""
        return {
            "Coordinator": cls.COORDINATOR_TESTS,
            "Schedule": cls.SCHEDULE_TESTS,
            "Task": cls.TASK_TESTS,
            "Code": cls.CODE_TESTS,
            "Translation": cls.TRANSLATION_TESTS,
            "Summary": cls.SUMMARY_TESTS,
            "Calculation": cls.CALCULATION_TESTS,
            "DataAnalysis": cls.DATA_ANALYSIS_TESTS,
        }
    
    @classmethod
    def get_agent_tests(cls, agent_name: str) -> List[Dict[str, Any]]:
        """获取特定Agent的测试数据"""
        all_tests = cls.get_all_tests()
        return all_tests.get(agent_name, [])
    
    @classmethod
    def get_total_test_count(cls) -> int:
        """获取测试用例总数"""
        all_tests = cls.get_all_tests()
        return sum(len(tests) for tests in all_tests.values())


# 评估标准
class EvaluationCriteria:
    """评估标准"""
    
    # Coordinator评估标准
    COORDINATOR_CRITERIA = {
        "agent_accuracy": "Agent选择准确率",
        "param_extraction": "参数提取完整性",
        "intent_recognition": "意图识别准确性"
    }
    
    # Schedule评估标准
    SCHEDULE_CRITERIA = {
        "time_extraction": "时间提取准确率",
        "participant_extraction": "参与者识别准确率",
        "repeat_pattern": "重复模式识别"
    }
    
    # Task评估标准
    TASK_CRITERIA = {
        "priority_judgment": "优先级判断准确率",
        "deadline_extraction": "截止日期提取",
        "tags_generation": "标签生成质量"
    }
    
    # Code评估标准
    CODE_CRITERIA = {
        "code_correctness": "代码正确性",
        "code_quality": "代码质量（注释、规范）",
        "explanation_clarity": "解释清晰度"
    }
    
    # 通用评估标准
    GENERAL_CRITERIA = {
        "output_format": "输出格式一致性",
        "completeness": "信息完整性",
        "relevance": "相关性"
    }
    
    @classmethod
    def get_criteria(cls, agent_name: str) -> Dict[str, str]:
        """获取特定Agent的评估标准"""
        criteria_map = {
            "Coordinator": cls.COORDINATOR_CRITERIA,
            "Schedule": cls.SCHEDULE_CRITERIA,
            "Task": cls.TASK_CRITERIA,
            "Code": cls.CODE_CRITERIA,
        }
        return {**criteria_map.get(agent_name, {}), **cls.GENERAL_CRITERIA}


# 预期提升目标
EXPECTED_IMPROVEMENTS = {
    "Coordinator": {
        "agent_accuracy": {"baseline": 0.70, "target": 0.90, "improvement": "+28.6%"},
        "param_extraction": {"baseline": 0.60, "target": 0.85, "improvement": "+41.7%"},
    },
    "Schedule": {
        "time_extraction": {"baseline": 0.75, "target": 0.95, "improvement": "+26.7%"},
        "repeat_pattern": {"baseline": 0.50, "target": 0.80, "improvement": "+60.0%"},
    },
    "Task": {
        "priority_judgment": {"baseline": 0.65, "target": 0.90, "improvement": "+38.5%"},
        "deadline_extraction": {"baseline": 0.70, "target": 0.90, "improvement": "+28.6%"},
    },
    "Code": {
        "code_quality": {"baseline": 0.70, "target": 0.90, "improvement": "+28.6%"},
        "explanation_clarity": {"baseline": 0.65, "target": 0.95, "improvement": "+46.2%"},
    },
    "Overall": {
        "output_consistency": {"baseline": 0.60, "target": 0.90, "improvement": "+50.0%"},
        "complex_task_handling": {"baseline": 0.50, "target": 0.80, "improvement": "+60.0%"},
    }
}


if __name__ == "__main__":
    # 打印数据集统计
    print("📊 基准测试数据集统计\n")
    print(f"总测试用例数: {BenchmarkDataset.get_total_test_count()}")
    print("\n各Agent测试用例分布:")
    for agent_name, tests in BenchmarkDataset.get_all_tests().items():
        print(f"  - {agent_name}: {len(tests)}个用例")
    
    print("\n\n🎯 预期提升目标:")
    for category, metrics in EXPECTED_IMPROVEMENTS.items():
        print(f"\n{category}:")
        for metric, values in metrics.items():
            print(f"  {metric}:")
            print(f"    基线: {values['baseline']:.0%}")
            print(f"    目标: {values['target']:.0%}")
            print(f"    提升: {values['improvement']}")
