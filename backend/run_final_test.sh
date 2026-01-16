#!/bin/bash
# 第三轮测试 - 验证完整修复效果

echo "================================"
echo "🔧 第三轮测试（完整修复版）"
echo "================================"
echo ""
echo "本轮修复："
echo "  ✅ 增强JSON解析（正则提取）"
echo "  ✅ 优化Fallback关键词（+50个）"
echo "  ✅ 扩展AGENT_MAP（支持别名）"
echo "  ✅ 明确task_type列表"
echo "  ✅ 更新Few-shot示例（5个）"
echo ""
echo "预期目标："
echo "  🎯 Agent选择准确率: 90%+ (当前60%)"
echo "  🎯 参数提取准确率: 75%+ (当前40%)"
echo ""
echo "重点关注case："
echo "  • '帮我写Python快速排序' → CodeAgent"
echo "  • '本周五前完成报告' → TaskAgent"
echo "  • '下周一9点和张三讨论' → ScheduleAgent"
echo "  • '总结这篇文章的要点' → SummaryAgent"
echo "  • '推荐几部科幻电影' → RecommendationAgent"
echo ""
echo "按Enter开始测试..."
read

cd /home/liu/program/jarvis/backend
python test_step3_accuracy.py
