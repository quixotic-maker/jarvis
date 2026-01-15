"""Agent功能示例展示脚本"""

# 展示所有Agent的功能和示例

AGENT_EXAMPLES = {
    "办公效率类": {
        "ScheduleAgent": [
            "明天下午3点开会讨论项目",
            "下周一早上9点和张三见面",
            "安排本周五的团队会议"
        ],
        "TaskAgent": [
            "添加待办：完成项目报告，优先级高，截止日期本周五",
            "创建任务：学习Python，标签：编程",
            "记录待办事项：购买生日礼物"
        ],
        "EmailAgent": [
            "给李总写一封关于项目进展的邮件",
            "撰写一封客户感谢信",
            "帮我写封邮件邀请同事参加会议"
        ],
        "MeetingAgent": [
            "安排明天下午2点的项目评审会议",
            "帮我整理刚才会议的纪要",
            "安排下周的团队周会"
        ],
        "FileAgent": [
            "帮我找所有PDF文档",
            "搜索包含'报告'的文件",
            "帮我整理桌面文件"
        ],
        "NoteAgent": [
            "创建笔记：今天的学习心得",
            "记录灵感：新产品创意想法",
            "搜索关于Python的笔记"
        ],
        "ReminderAgent": [
            "明天早上8点提醒我开会",
            "每天下午6点提醒我下班",
            "下周五提醒我交报告"
        ]
    },
    
    "技术开发类": {
        "CodeAgent": [
            "用Python写一个快速排序算法",
            "解释这段代码的功能：[代码]",
            "优化这段代码的性能：[代码]"
        ],
        "DataAnalysisAgent": [
            "分析这组销售数据的趋势",
            "帮我做数据统计分析",
            "找出数据中的异常值"
        ],
        "CalculationAgent": [
            "计算 1234 * 5678 + 999",
            "求解方程 2x + 3 = 11",
            "计算投资回报率"
        ]
    },
    
    "学习成长类": {
        "LearningAgent": [
            "帮我制定Python学习计划",
            "解释机器学习的核心概念",
            "生成数据结构的测验题"
        ],
        "InfoRetrievalAgent": [
            "什么是多Agent系统？",
            "解释RESTful API",
            "Python和Java的区别"
        ]
    },
    
    "生活服务类": {
        "WeatherAgent": [
            "北京今天天气怎么样？",
            "上海明天会下雨吗？",
            "查询本周天气预报"
        ],
        "NewsAgent": [
            "今天有什么科技新闻？",
            "最新的AI资讯",
            "给我看看财经新闻"
        ],
        "TravelAgent": [
            "帮我规划北京三日游",
            "推荐适合周末的旅游景点",
            "制定日本7日游行程"
        ],
        "HealthAgent": [
            "给我一个减肥的运动计划",
            "健康饮食建议",
            "如何改善睡眠质量"
        ],
        "RecommendationAgent": [
            "推荐几部科幻电影",
            "有什么好看的编程书籍",
            "推荐适合放松的音乐"
        ],
        "TranslationAgent": [
            "把'Hello World'翻译成中文",
            "将这段话翻译成英文：[文本]",
            "Translate to Japanese"
        ],
        "SummaryAgent": [
            "总结这篇文章：[长文本]",
            "提取关键要点",
            "用一句话概括这段内容"
        ],
        "ContactAgent": [
            "添加联系人：张三，电话138xxxx，公司XX科技",
            "搜索李经理的联系方式",
            "查找所有在XX公司的联系人"
        ]
    }
}


def display_agent_examples():
    """展示所有Agent示例"""
    print("=" * 80)
    print("🤖 Jarvis - 21个智能Agent功能示例")
    print("=" * 80)
    print()
    
    total_agents = 0
    for category, agents in AGENT_EXAMPLES.items():
        print(f"\n{'='*80}")
        print(f"📂 {category} ({len(agents)}个Agent)")
        print(f"{'='*80}\n")
        
        for agent_name, examples in agents.items():
            total_agents += 1
            print(f"  🔸 {agent_name}")
            print(f"     示例用法：")
            for i, example in enumerate(examples, 1):
                print(f"       {i}. \"{example}\"")
            print()
    
    print("=" * 80)
    print(f"✨ 总计: {total_agents} 个专业Agent，覆盖工作、学习、生活全场景")
    print("=" * 80)
    print()
    print("💡 使用提示：")
    print("   - 在仪表板直接输入自然语言指令")
    print("   - 主控Agent会自动识别意图并调用对应Agent")
    print("   - 支持中英文混合输入")
    print("   - 可以组合使用多个Agent完成复杂任务")
    print()


if __name__ == "__main__":
    display_agent_examples()
