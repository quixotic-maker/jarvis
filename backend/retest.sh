#!/bin/bash
# 快速重新测试脚本

echo "================================"
echo "🔧 重新运行测试（修复后）"
echo "================================"
echo ""
echo "修复内容："
echo "  ✅ 增强JSON解析（正则提取）"
echo "  ✅ 优化Fallback关键词"
echo "  ✅ 强化Prompt约束"
echo ""
echo "按Enter开始测试..."
read

cd /home/liu/program/jarvis/backend
python test_full_suite.py
