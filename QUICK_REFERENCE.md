# 🚀 Jarvis快速参考指南

## 一句话总结
**Jarvis = 25个智能Agent + 知识图谱 + Agentic RAG + MCP协议**

---

## 📋 速查表

### Agent分类（25个）

| 类别 | Agent数量 | 代表Agent |
|------|----------|-----------|
| 办公效率 | 7个 | Schedule, Task, Email |
| 技术开发 | 3个 | Code, DataAnalysis |
| 学习成长 | 2个 | Learning, InfoRetrieval |
| 生活服务 | 9个 | Weather, News, Travel |
| 高级AI | 4个 | KnowledgeGraph, AgenticRAG |
| 核心协调 | 1个 | Coordinator |

### 核心技术

```
🧠 知识图谱 - 结构化知识表示
📚 RAG - 检索增强生成
🤖 Agentic RAG - 主动式智能检索（⭐核心亮点）
🔌 MCP - 模型上下文协议
💬 LLM - GPT-4 + Claude双引擎
```

---

## ⚡ 快速命令

### 启动项目
```bash
# 1. Backend
cd backend
uvicorn main:app --reload --port 8000

# 2. Frontend
cd frontend
npm run dev
```

### 测试Agent
```bash
cd backend

# 测试所有基础Agent
python show_agents.py

# 测试高级Agent
python test_advanced_agents.py
```

### API文档
```bash
# 访问交互式API文档
http://localhost:8000/docs

# 访问ReDoc文档
http://localhost:8000/redoc
```

---

## 🔌 常用API

### 基础功能
```bash
# 创建任务（自动路由到对应Agent）
POST /api/tasks
{
    "user_input": "明天下午3点开会"
}

# 查询日程
GET /api/schedules

# Agent日志
GET /api/agents/logs
```

### 🆕 高级功能

#### 知识图谱
```bash
# 提取知识
POST /api/advanced/knowledge-graph/extract
{
    "text": "深度学习是机器学习的分支..."
}

# 查询图谱
POST /api/advanced/knowledge-graph/query
{
    "query": "深度学习"
}
```

#### Agentic RAG（⭐推荐）
```bash
# 高级查询（自动迭代优化）
POST /api/advanced/agentic-rag/query
{
    "query": "对比React和Vue，给出选型建议",
    "max_iterations": 3
}
```

#### MCP对话
```bash
# 上下文对话
POST /api/advanced/mcp/chat
{
    "message": "帮我安排会议",
    "context": {"user_id": "user123"}
}
```

---

## 🎯 使用场景

### 办公场景
```python
"明天下午2点和李总开会，讨论Q1规划"  → ScheduleAgent + MeetingAgent
"给客户写一封道歉邮件"                 → EmailAgent
"提醒我下周五交报告"                   → ReminderAgent
```

### 技术场景
```python
"用Python实现快速排序"                 → CodeAgent
"分析这组销售数据的趋势"               → DataAnalysisAgent
"计算投资回报率"                       → CalculationAgent
```

### 学习场景
```python
"制定Python学习计划"                   → LearningAgent
"什么是微服务架构？"                   → InfoRetrievalAgent + RAGAgent
"解释机器学习的核心概念"               → InfoRetrievalAgent
```

### 🆕 高级场景
```python
"对比分析React和Vue，给出选型建议"      → AgenticRAGAgent (迭代检索)
"构建关于深度学习的知识图谱"           → KnowledgeGraphAgent
"基于文档回答：如何优化数据库性能？"   → RAGAgent
"继续刚才的话题"                       → MCPAgent (上下文对话)
```

---

## 📊 文件结构速览

```
jarvis/
├── backend/
│   ├── main.py                          # 🚀 启动入口
│   ├── app/
│   │   ├── agents/
│   │   │   ├── [25个Agent文件]
│   │   │   ├── agentic_rag_agent.py     # ⭐ 核心Agent
│   │   │   └── __init__.py              # Agent注册表
│   │   ├── api/endpoints/
│   │   │   └── advanced_agents.py       # 🆕 高级API
│   │   └── db/models.py                 # 15个数据表
│   └── test_advanced_agents.py          # 🆕 测试脚本
│
├── frontend/
│   ├── src/
│   │   ├── pages/Dashboard.tsx          # 主页面
│   │   └── api/client.ts                # API客户端
│
├── README.md                             # 📖 项目概览
├── AGENTS.md                             # 📚 Agent详解
├── ADVANCED_AGENTS.md                    # 🆕 高级技术
├── ARCHITECTURE.md                       # 🏗️ 架构设计
├── PROJECT_SUMMARY.md                    # 📊 成果总览
└── QUICK_REFERENCE.md                    # ⚡ 本文档
```

---

## 🔧 配置要点

### 环境变量（.env）
```bash
# LLM配置
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 数据库配置
DATABASE_URL=sqlite:///./jarvis.db

# 服务器配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 关键配置文件
```bash
backend/app/core/config.py    # 后端配置
frontend/vite.config.ts       # 前端构建配置
```

---

## 🎓 学习路径

### 🔰 入门级（1-2小时）
1. 阅读 [README.md](README.md)
2. 运行 `show_agents.py`
3. 访问 http://localhost:8000/docs
4. 尝试几个简单的API调用

### 🎯 进阶级（半天）
1. 阅读 [AGENTS.md](AGENTS.md)
2. 研究Coordinator的任务路由逻辑
3. 测试各类Agent的功能
4. 了解前端页面结构

### 🚀 高级级（1天）
1. 阅读 [ADVANCED_AGENTS.md](ADVANCED_AGENTS.md)
2. 深入理解Agentic RAG原理
3. 研究知识图谱构建过程
4. 学习MCP协议实现

### 💎 专家级（2-3天）
1. 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)
2. 理解完整的技术架构
3. 自定义新的Agent
4. 优化和扩展功能

---

## 💡 常见问题

### Q1: 如何添加新的Agent？
```python
# 1. 创建新Agent文件
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent", description="...")
    
    async def execute(self, input_data):
        # 实现逻辑
        pass

# 2. 在 __init__.py 注册
from app.agents.my_agent import MyAgent
AGENT_REGISTRY["MyAgent"] = MyAgent

# 3. 更新Coordinator的路由逻辑
```

### Q2: Agentic RAG和普通RAG的区别？
```
普通RAG: 单次检索 → 生成答案
Agentic RAG: 规划 → 迭代检索 → 反思 → 优化 → 生成
             ↑                              ↓
             └──── 质量不足时循环 ────────────┘
```

### Q3: 如何提高RAG的准确性？
1. 提供更多高质量文档
2. 优化文档分块策略
3. 使用Agentic RAG（自动优化）
4. 调整max_iterations参数

### Q4: 知识图谱的最佳实践？
- 使用清晰的实体命名
- 定义标准的关系类型
- 保持图谱更新
- 利用推理能力查询

---

## 📈 性能优化

### 提升响应速度
```python
# 1. 使用缓存
- LLM响应缓存
- API结果缓存

# 2. 并发处理
- 异步Agent执行
- 批量操作

# 3. 数据库优化
- 添加索引
- 查询优化
```

### 降低成本
```python
# 1. LLM调用优化
- 缓存相似查询
- 使用更经济的模型

# 2. 智能路由
- 简单任务用规则
- 复杂任务用LLM
```

---

## 🔒 安全建议

```bash
# 1. API密钥管理
- 使用环境变量
- 不要提交到Git

# 2. 输入验证
- 验证用户输入
- 防止提示词注入

# 3. 权限控制
- 实现用户认证
- API访问限流
```

---

## 🎯 核心优势

### 相比其他Agent系统
✅ **Agent数量**: 25个（业界领先）  
✅ **技术先进**: Agentic RAG（前沿技术）  
✅ **架构完整**: 前后端分离 + 数据库 + AI  
✅ **文档详尽**: 5份专业文档  
✅ **可扩展性**: 模块化设计  

### 核心竞争力
⭐ **Agentic RAG** - 自主迭代优化的智能检索  
⭐ **知识图谱** - 结构化知识表示  
⭐ **MCP协议** - 标准化上下文管理  
⭐ **25个Agent** - 全场景覆盖  

---

## 🚀 快速测试

### 5分钟快速体验
```bash
# 1. 启动服务
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev &

# 2. 访问
open http://localhost:5173

# 3. 在Dashboard输入
"帮我分析React和Vue的优缺点"
```

### 10分钟完整测试
```bash
# 运行完整测试套件
cd backend
python test_advanced_agents.py

# 查看结果：
# - 知识图谱测试 ✅
# - RAG测试 ✅
# - Agentic RAG测试 ✅
# - MCP测试 ✅
```

---

## 📞 获取帮助

### 文档导航
| 需求 | 查看文档 |
|------|---------|
| 快速了解 | [README.md](README.md) |
| Agent功能 | [AGENTS.md](AGENTS.md) |
| 高级技术 | [ADVANCED_AGENTS.md](ADVANCED_AGENTS.md) |
| 架构设计 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 项目总览 | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| 快速参考 | 本文档 |

### API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🎉 开始使用

### 方式1: 交互式API
```bash
# 访问Swagger UI
http://localhost:8000/docs

# 点击"Try it out"测试API
```

### 方式2: 前端界面
```bash
# 访问Dashboard
http://localhost:5173

# 在输入框输入自然语言
```

### 方式3: 命令行测试
```bash
cd backend
python test_advanced_agents.py
```

---

## ⭐ 推荐功能

### 必试功能TOP 3

#### 🥇 Agentic RAG查询
```bash
POST /api/advanced/agentic-rag/query
{
    "query": "对比React和Vue，分析优缺点并给出选型建议",
    "max_iterations": 3
}

# 特点：自动迭代优化，返回推理链，高质量答案
```

#### 🥈 知识图谱构建
```bash
POST /api/advanced/knowledge-graph/build
{
    "topic": "深度学习"
}

# 特点：自动抽取实体和关系，构建知识网络
```

#### 🥉 MCP上下文对话
```bash
POST /api/advanced/mcp/chat
{
    "message": "继续刚才的话题",
    "context": {"user_id": "user123"}
}

# 特点：智能上下文管理，对话连贯性强
```

---

## 📊 技术指标

| 指标 | 数值 |
|------|------|
| Agent总数 | 25个 |
| 数据表数 | 15个 |
| API端点 | 20+ |
| 代码文件 | 60+ |
| 文档数 | 6份 |
| 支持LLM | 2个 |

---

## 🎯 记住这些

```
✅ 25个Agent = 办公(7) + 技术(3) + 学习(2) + 生活(9) + AI(4)
✅ 高级AI = 知识图谱 + RAG + Agentic RAG + MCP
✅ 核心亮点 = Agentic RAG（迭代优化 + 自我反思）
✅ 快速开始 = uvicorn + npm run dev
✅ API文档 = /docs
```

---

**祝使用愉快！有问题查看详细文档 📚**
