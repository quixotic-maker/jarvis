# Jarvis用户手册

## 📖 目录
- [快速入门](#快速入门)
- [知识库管理](#知识库管理)
- [Agent使用](#agent使用)
- [API使用指南](#api使用指南)
- [常见问题](#常见问题)

---

## 快速入门

### 首次使用

**1. 访问系统**
- 打开浏览器访问: `http://localhost:3000`
- 或生产环境: `https://yourdomain.com`

**2. 界面概览**
```
┌─────────────────────────────────────┐
│  Jarvis - 智能助手系统               │
├─────────────────────────────────────┤
│ 🏠 首页  📚 知识库  🤖 Agent  ⚙️ 设置│
├─────────────────────────────────────┤
│                                     │
│   [聊天输入框]                       │
│                                     │
│   Agent响应区域                      │
│                                     │
└─────────────────────────────────────┘
```

**3. 基本对话**
```
用户: 你好，Jarvis
Jarvis: 您好！我是Jarvis，您的智能助手。我可以帮您：
  • 管理日程和任务
  • 查询信息和天气
  • 翻译和总结文本
  • 代码辅助
  请问有什么可以帮到您？
```

---

## 知识库管理

### 创建知识库

**通过UI界面**

1. 点击顶部导航 `📚 知识库`
2. 点击 `+ 新建知识库` 按钮
3. 填写信息：
   - **名称**: `python_docs`（英文，无空格）
   - **描述**: `Python官方文档`
   - **分块大小**: 800（默认）
   - **分块重叠**: 150（默认）
4. 点击 `创建`

**通过API**
```bash
curl -X POST http://localhost:8000/api/knowledge-base/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "python_docs",
    "description": "Python官方文档",
    "chunk_size": 800,
    "chunk_overlap": 150
  }'
```

### 添加文档

**方式一：上传文件**

1. 进入知识库详情页
2. 点击 `上传文档` 按钮
3. 拖拽文件或点击选择
4. 支持格式：
   - 文本: `.txt`, `.md`
   - 代码: `.py`, `.js`, `.ts`, `.java`, `.cpp`
   - 文档: `.pdf`（需要额外配置）

**方式二：添加文本**

点击 `添加文本` → 输入内容 → 保存

```
标题: Python基础
内容: Python是一种解释型的高级编程语言...
标签: programming, python, basics
```

**方式三：批量导入**

API方式批量导入目录：
```bash
curl -X POST http://localhost:8000/api/knowledge-base/python_docs/import \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/path/to/docs",
    "file_patterns": ["*.txt", "*.md"],
    "recursive": true
  }'
```

### 搜索知识库

**四种搜索模式**

1. **语义搜索** (Semantic)
   - 基于向量相似度
   - 理解语义关系
   - 适合：概念性查询

   ```
   查询: "如何学习机器学习"
   结果: 返回所有关于机器学习、深度学习、AI的相关文档
   ```

2. **关键词搜索** (Keyword)
   - 基于关键词匹配
   - BM25算法
   - 适合：精确查找

   ```
   查询: "Python class 定义"
   结果: 返回包含"Python"和"class"的文档
   ```

3. **混合搜索** (Hybrid)
   - 语义 + 关键词
   - 综合优势
   - **推荐使用**

4. **重排序** (Rerank)
   - 二次精排
   - 最高精度
   - 速度稍慢

**使用示例**

界面操作：
1. 点击知识库卡片的 `🔍 搜索` 按钮
2. 输入查询内容
3. 选择搜索模式
4. 设置结果数量（3/5/10/20）
5. 点击 `搜索`

查看结果：
```
┌────────────────────────────────┐
│ #1  相关度: 85%  ⭐⭐⭐⭐⭐     │
├────────────────────────────────┤
│ Python是一种解释型语言...       │
│ 标签: programming, python      │
└────────────────────────────────┘
```

### 管理知识库

**查看统计**
- 文档数量
- 总字符数
- 最后更新时间

**导出知识库**
```bash
curl -X POST http://localhost:8000/api/knowledge-base/python_docs/export \
  -o export.json
```

**删除知识库**
⚠️ 此操作会清空所有文档！
1. 点击知识库卡片的 `🗑️ 删除` 按钮
2. 确认删除

---

## Agent使用

### 可用Agent列表

Jarvis拥有**21个专业Agent**：

#### 📋 办公效率类
- **ScheduleAgent**: 日程管理
- **TaskAgent**: 任务管理
- **EmailAgent**: 邮件助手
- **MeetingAgent**: 会议管理
- **FileAgent**: 文件管理
- **NoteAgent**: 笔记管理
- **ReminderAgent**: 提醒管理

#### 💻 技术开发类
- **CodeAgent**: 代码助手
- **DataAnalysisAgent**: 数据分析
- **CalculationAgent**: 计算器

#### 📚 学习成长类
- **LearningAgent**: 学习助手
- **InfoRetrievalAgent**: 信息检索

#### 🌍 生活服务类
- **WeatherAgent**: 天气查询
- **NewsAgent**: 新闻资讯
- **TravelAgent**: 旅行规划
- **HealthAgent**: 健康管理
- **RecommendationAgent**: 推荐系统
- **TranslationAgent**: 翻译服务
- **SummaryAgent**: 文本总结
- **ContactAgent**: 联系人管理

### 使用示例

**日程管理**
```
用户: 明天下午3点提醒我开会
Jarvis: ✅ 已创建日程：
  • 标题: 开会
  • 时间: 2026-01-17 15:00
  • 状态: 已安排
```

**任务管理**
```
用户: 添加待办：完成RAG系统文档，优先级高
Jarvis: ✅ 已添加任务：
  • 内容: 完成RAG系统文档
  • 优先级: 高
  • 状态: 待完成
```

**代码助手**
```
用户: 用Python写一个快速排序算法
Jarvis: 这里是快速排序的Python实现：

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# 使用示例
arr = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(arr))
# 输出: [1, 1, 2, 3, 6, 8, 10]
```

**翻译服务**
```
用户: 把"Good morning"翻译成中文
Jarvis: "Good morning" 的中文翻译是：早上好
```

**文本总结**
```
用户: 总结这段文字：[长文本]
Jarvis: 📝 内容总结：
主要观点：
1. ...
2. ...
3. ...
```

### 智能任务分发

Jarvis的**Coordinator Agent**会自动：
1. 分析用户意图
2. 选择合适的Agent
3. 提取必要参数
4. 执行并返回结果

你只需自然对话，无需指定Agent！

---

## API使用指南

### 认证（如已启用）

```bash
# 获取token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# 使用token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/knowledge-base/
```

### 知识库API

**创建知识库**
```bash
POST /api/knowledge-base/
{
  "name": "my_kb",
  "description": "My Knowledge Base",
  "chunk_size": 800,
  "chunk_overlap": 150
}
```

**添加文本**
```bash
POST /api/knowledge-base/my_kb/text
{
  "text": "Your document content here...",
  "metadata": {
    "category": "documentation",
    "author": "John Doe"
  }
}
```

**搜索文档**
```bash
POST /api/knowledge-base/my_kb/search
{
  "query": "machine learning",
  "mode": "hybrid",
  "k": 5,
  "filter_metadata": {
    "category": "ai"
  }
}
```

**上传文件**
```bash
curl -X POST \
  -F "file=@document.txt" \
  -F "metadata={\"category\":\"docs\"}" \
  http://localhost:8000/api/knowledge-base/my_kb/upload
```

**列出文档**
```bash
GET /api/knowledge-base/my_kb/documents?limit=10
```

**获取统计**
```bash
GET /api/knowledge-base/my_kb/stats
```

**删除知识库**
```bash
DELETE /api/knowledge-base/my_kb
```

### 缓存管理API

**查看缓存统计**
```bash
GET /api/knowledge-base/cache/stats
```

**清空缓存**
```bash
POST /api/knowledge-base/cache/clear
```

### 完整API文档

访问交互式API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 常见问题

### 功能相关

**Q: 支持哪些文件格式？**
A: 目前支持 .txt, .md, .py, .js, .ts, .java, .cpp 等文本文件。PDF支持需额外配置pypdf库。

**Q: 知识库可以存储多少文档？**
A: 无硬性限制，受限于磁盘空间。建议单个知识库不超过10,000个文档以保持性能。

**Q: 搜索结果不准确怎么办？**
A: 尝试：
1. 切换到混合搜索模式
2. 调整分块大小（更小的chunk_size）
3. 增加结果数量（k值）
4. 使用更精确的查询词

**Q: 如何提高搜索速度？**
A: 
1. 启用缓存（已默认启用5分钟TTL）
2. 使用语义搜索而非重排序
3. 减少返回结果数量
4. 为文档添加元数据过滤

### 技术问题

**Q: 如何切换Embedding模型？**
A: 修改.env文件：
```bash
EMBEDDING_PROVIDER=local  # 或 openai
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Q: API返回401错误**
A: 检查认证token是否有效，或确认API是否需要认证。

**Q: 上传大文件失败**
A: 修改Nginx配置：
```nginx
client_max_body_size 100M;
```

**Q: 向量数据存储在哪里？**
A: 
- Docker: `/app/data/vector_stores` (容器内)
- 本地: `./backend/data/vector_stores`

### 性能优化

**Q: 如何优化大规模知识库性能？**
A:
1. 使用元数据过滤减少搜索范围
2. 启用Redis缓存
3. 增加embedding batch size
4. 使用更快的向量数据库（如Qdrant）

**Q: 内存占用过高怎么办？**
A:
1. 减少并发worker数量
2. 限制最大文档缓存数
3. 使用外部向量数据库

---

## 最佳实践

### 知识库设计

1. **合理分类**
   - 为不同主题创建独立知识库
   - 使用元数据标签分类文档

2. **优化文档质量**
   - 去除无关内容
   - 保持格式一致
   - 添加丰富的元数据

3. **定期维护**
   - 删除过时文档
   - 更新重要内容
   - 监控搜索质量

### 搜索技巧

1. **使用具体查询**
   ```
   ❌ 不好: "Python"
   ✅ 好: "Python列表推导式的用法"
   ```

2. **组合元数据过滤**
   ```json
   {
     "query": "深度学习",
     "filter_metadata": {
       "category": "ai",
       "year": "2024"
     }
   }
   ```

3. **选择合适的搜索模式**
   - 学习类: 语义搜索
   - 查找特定术语: 关键词搜索
   - 综合查询: 混合搜索
   - 要求高精度: 重排序

---

## 更多资源

- 📘 完整文档: https://docs.jarvis.ai
- 🎓 视频教程: https://youtube.com/jarvis-ai
- 💬 社区论坛: https://community.jarvis.ai
- 📧 技术支持: support@jarvis.ai

---

**祝您使用愉快！🎉**
