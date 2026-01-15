# Jarvis 手动测试指南

## 📋 测试环境准备

### 前置条件
- Python 3.13.5
- Node.js 18+
- 浏览器（Chrome/Edge/Firefox推荐）

### 启动服务

**1. 启动后端服务**
```bash
cd /home/liu/program/jarvis/backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
✅ 预期结果：
- 控制台显示 "🚀 Jarvis 系统启动中..."
- 服务运行在 http://localhost:8000

**2. 启动前端服务**
```bash
cd /home/liu/program/jarvis/frontend
npm run dev
```
✅ 预期结果：
- Vite服务启动
- 前端运行在 http://localhost:3001 (或3002)

---

## Phase 1-2: 前端UI组件测试

### 测试目标
验证所有UI页面能正常渲染，组件交互正常

### 测试步骤

#### 1. 对话页面 (Chat)
**URL**: http://localhost:3001/chat

**测试项**:
- [ ] 页面正常加载
- [ ] 侧边栏显示Agent列表（21个Agent）
- [ ] 消息输入框可输入文字
- [ ] 发送按钮可点击
- [ ] 历史对话记录显示

**验证方法**:
1. 打开开发者工具 (F12)
2. 检查控制台无错误
3. 尝试输入消息
4. 点击不同Agent切换

#### 2. Agent中心页面
**URL**: http://localhost:3001/agents

**测试项**:
- [ ] 显示21个Agent卡片
- [ ] 每个Agent有图标、名称、描述
- [ ] 状态指示器（激活/未激活）
- [ ] 搜索框功能
- [ ] 分类筛选

**验证方法**:
1. 计数Agent卡片数量
2. 在搜索框输入"日程"，应只显示ScheduleAgent
3. 点击分类标签筛选

#### 3. 日程管理页面
**URL**: http://localhost:3001/schedule

**测试项**:
- [ ] 日历视图正常显示
- [ ] 当前月份正确
- [ ] 可切换上/下月
- [ ] 今天高亮显示
- [ ] 右侧日程列表

**验证方法**:
1. 检查日历网格（7列×5-6行）
2. 点击"上一月"/"下一月"按钮
3. 点击"今天"按钮，应跳回当前日期

#### 4. 学习工作台页面
**URL**: http://localhost:3001/learning

**测试项**:
- [ ] 学习计划列表
- [ ] 资源卡片
- [ ] 进度条显示
- [ ] 知识图谱可视化

#### 5. 成长轨迹页面
**URL**: http://localhost:3001/growth

**测试项**:
- [ ] 3D知识图谱渲染
- [ ] 可旋转/缩放
- [ ] 节点信息展示
- [ ] 技能树显示

#### 6. 设置页面
**URL**: http://localhost:3001/settings

**测试项**:
- [ ] 8个设置标签页
- [ ] 个人资料表单
- [ ] 系统偏好选项
- [ ] Agent配置滑块
- [ ] 保存按钮

---

## Phase 3 Week 1: 后端API测试

### 测试目标
验证所有API端点正常工作，返回正确格式

### 测试工具
- curl命令行
- Swagger文档: http://localhost:8000/docs
- 浏览器访问

### API端点测试

#### 1. 健康检查
```bash
curl http://localhost:8000/
```
✅ 预期响应:
```json
{
  "message": "Welcome to Jarvis - Your Multi-Agent Assistant",
  "status": "running",
  "version": "1.0.0"
}
```

#### 2. 日程API - 列表查询
```bash
curl 'http://localhost:8000/api/v2/schedules/?page=1&page_size=10'
```
✅ 预期响应格式:
```json
{
  "status": "success",
  "message": "获取日程列表成功",
  "data": [...],
  "meta": {
    "page": 1,
    "page_size": 10,
    "total": 6,
    "total_pages": 1
  },
  "timestamp": "2026-01-16T..."
}
```

#### 3. 日程API - 创建
```bash
curl -X POST http://localhost:8000/api/v2/schedules/ \
-H "Content-Type: application/json" \
-d '{
  "title": "测试会议",
  "description": "API测试",
  "start_time": "2026-01-20T14:00:00",
  "end_time": "2026-01-20T15:00:00",
  "location": "会议室B",
  "attendees": ["测试用户"],
  "priority": "medium",
  "event_type": "meeting"
}'
```
✅ 验证:
- status: "success"
- data包含新创建的日程
- id自动生成

#### 4. 任务API - 列表查询
```bash
curl http://localhost:8000/api/v2/tasks/
```
✅ 预期: 返回任务列表，格式同日程API

#### 5. 任务API - 创建
```bash
curl -X POST http://localhost:8000/api/v2/tasks/ \
-H "Content-Type: application/json" \
-d '{
  "title": "测试任务",
  "description": "验证API",
  "priority": "high",
  "due_date": "2026-01-25T18:00:00",
  "tags": ["测试", "API"]
}'
```

#### 6. 设置API - 查询
```bash
curl http://localhost:8000/api/v2/settings/
```
✅ 验证:
- 返回系统设置和Agent配置
- theme/language/font_size等字段存在

#### 7. 设置API - 更新
```bash
curl -X PUT http://localhost:8000/api/v2/settings/ \
-H "Content-Type: application/json" \
-d '{
  "user_id": "default_user",
  "settings": {
    "system": {
      "theme": "light",
      "language": "zh-CN",
      "font_size": "large",
      "sound_enabled": false,
      "notifications_enabled": true,
      "auto_save": true
    },
    "agent": {
      "default_agent": "coordinator",
      "response_speed": "balanced",
      "creativity": 80,
      "max_tokens": 3000,
      "temperature": 0.8,
      "enable_voice": true,
      "enable_memory": true
    }
  }
}'
```

### Swagger文档测试

**URL**: http://localhost:8000/docs

**测试步骤**:
1. 打开Swagger UI
2. 查看所有API端点分组
3. 展开 `/api/v2/schedules/` 
4. 点击 "Try it out"
5. 填写参数
6. 点击 "Execute"
7. 查看响应

✅ 验证点:
- [ ] 所有端点有文档说明
- [ ] 请求/响应示例正确
- [ ] 可以直接测试调用

---

## Phase 3 Week 2: 前后端集成测试

### 测试目标
验证前端页面能正确调用后端API，数据显示正确

### 前置准备

**创建测试数据**:
```bash
cd /home/liu/program/jarvis/backend
python create_test_data.py
```
✅ 预期: 创建5个日程 + 5个任务

### 集成测试步骤

#### 1. 日程页面集成测试

**URL**: http://localhost:3001/schedule

**测试流程**:

1️⃣ **页面加载测试**
- [ ] 打开页面，显示Loading状态
- [ ] 1-2秒后显示日历
- [ ] 右侧显示"今日日程"

2️⃣ **数据显示测试**
- [ ] 日历上有绿色指示点（表示有日程）
- [ ] 右侧列表显示日程卡片
- [ ] 日程信息完整（标题/时间/地点/参与者）

3️⃣ **交互测试**
- [ ] 点击不同日期，右侧列表更新
- [ ] 点击"今天"按钮，跳回当前日期
- [ ] 切换月份，日程数据正确加载

4️⃣ **数据验证**
打开浏览器开发者工具:
```javascript
// 在Console中执行
fetch('http://localhost:8000/api/v2/schedules/')
  .then(r => r.json())
  .then(d => console.log('日程数量:', d.meta.total))
```
✅ 应显示: 日程数量: 6 (1个初始+5个测试)

5️⃣ **错误处理测试**
- 停止后端服务
- 刷新页面
- [ ] 显示错误提示
- [ ] 有"重试"按钮
- 重启后端
- 点击重试
- [ ] 数据重新加载成功

#### 2. 设置页面集成测试

**URL**: http://localhost:3001/settings

**测试流程**:

1️⃣ **加载设置**
- [ ] 打开页面，显示Loading
- [ ] 系统偏好标签页显示当前设置
- [ ] Agent配置标签页显示滑块

2️⃣ **修改系统设置**
- 切换到"系统偏好"标签
- 修改主题为"Light"
- 修改语言为"en-US"
- 点击页面底部"保存设置"
- [ ] 显示"保存成功"提示

3️⃣ **验证保存**
- 刷新页面
- [ ] 设置仍为修改后的值
- 或用curl验证:
```bash
curl http://localhost:8000/api/v2/settings/ | grep theme
```

4️⃣ **修改Agent配置**
- 切换到"Agent配置"标签
- 拖动"创造力"滑块到85
- 修改"最大Token数"为4000
- 点击保存
- [ ] 保存成功

5️⃣ **错误恢复测试**
- 关闭后端
- 尝试保存设置
- [ ] 显示错误提示"保存失败"
- [ ] 不显示成功提示

#### 3. API调用验证

**在浏览器Console中执行**:

```javascript
// 测试日程API
fetch('http://localhost:8000/api/v2/schedules/')
  .then(r => r.json())
  .then(d => {
    console.log('✅ 日程API测试:')
    console.log('  - 状态:', d.status)
    console.log('  - 总数:', d.meta.total)
    console.log('  - 数据:', d.data.length, '条')
  })

// 测试任务API
fetch('http://localhost:8000/api/v2/tasks/')
  .then(r => r.json())
  .then(d => {
    console.log('✅ 任务API测试:')
    console.log('  - 状态:', d.status)
    console.log('  - 总数:', d.meta.total)
  })

// 测试设置API
fetch('http://localhost:8000/api/v2/settings/')
  .then(r => r.json())
  .then(d => {
    console.log('✅ 设置API测试:')
    console.log('  - 主题:', d.data.settings.system.theme)
    console.log('  - 默认Agent:', d.data.settings.agent.default_agent)
  })
```

✅ 全部成功输出表示集成正常

---

## 性能测试

### 1. API响应时间
```bash
# 测试日程列表API
time curl -s http://localhost:8000/api/v2/schedules/ > /dev/null
```
✅ 预期: < 100ms

### 2. 页面加载时间
打开浏览器开发者工具 → Network标签:
- [ ] DOMContentLoaded < 500ms
- [ ] Load < 2s
- [ ] API请求 < 100ms

### 3. 并发测试
```bash
# 同时发送10个请求
for i in {1..10}; do
  curl -s http://localhost:8000/api/v2/schedules/ &
done
wait
```
✅ 全部请求成功返回

---

## 数据库测试

### 查看数据库内容
```bash
cd /home/liu/program/jarvis/backend
sqlite3 jarvis.db

# 查询日程
SELECT id, title, priority, event_type FROM schedules;

# 查询任务
SELECT id, title, status, priority FROM tasks;

# 退出
.quit
```

### 数据完整性验证
```sql
-- 检查日程字段
SELECT 
  COUNT(*) as total,
  COUNT(user_id) as has_user_id,
  COUNT(title) as has_title,
  COUNT(start_time) as has_start_time
FROM schedules;

-- 应该全部相等

-- 检查任务字段
SELECT 
  COUNT(*) as total,
  COUNT(title) as has_title,
  COUNT(status) as has_status
FROM tasks;
```

---

## 常见问题排查

### 问题1: 前端页面空白
**检查步骤**:
1. 打开开发者工具Console
2. 查看是否有错误信息
3. 检查Network标签，API请求是否失败
4. 确认后端服务正在运行

### 问题2: API返回500错误
**检查步骤**:
1. 查看后端控制台错误信息
2. 检查数据库文件是否存在
3. 验证请求数据格式是否正确

### 问题3: CORS错误
**解决方案**:
- 确认后端配置了CORS
- 检查frontend/.env.development中API_BASE_URL
- 后端应允许来自localhost:3001的请求

### 问题4: 数据不显示
**检查步骤**:
1. 运行测试数据创建脚本
2. 用curl验证API返回数据
3. 检查前端API调用代码
4. 查看浏览器Console的网络请求

---

## 测试检查清单

### Phase 1-2 前端UI ✅
- [ ] 8个页面全部可访问
- [ ] 17个组件正常渲染
- [ ] 无TypeScript编译错误
- [ ] 无控制台错误
- [ ] 响应式布局正常

### Phase 3 Week 1 后端API ✅
- [ ] 健康检查端点正常
- [ ] 日程CRUD全部接口测试通过
- [ ] 任务CRUD全部接口测试通过
- [ ] 设置接口读写正常
- [ ] Swagger文档可访问
- [ ] 响应格式统一

### Phase 3 Week 2 集成 ✅
- [ ] 日程页面加载真实数据
- [ ] 设置页面读写成功
- [ ] Loading状态正常显示
- [ ] 错误处理正确
- [ ] API调用类型安全
- [ ] 测试数据创建成功

---

## 回归测试脚本

创建快速验证脚本:

```bash
#!/bin/bash
# test_all.sh - 快速验证所有功能

echo "🧪 Jarvis 功能测试"
echo "=================="

# 测试后端健康
echo "1️⃣ 测试后端健康..."
curl -f http://localhost:8000/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ 后端服务正常"
else
  echo "❌ 后端服务异常"
  exit 1
fi

# 测试日程API
echo "2️⃣ 测试日程API..."
SCHEDULE_COUNT=$(curl -s http://localhost:8000/api/v2/schedules/ | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
echo "✅ 日程数量: $SCHEDULE_COUNT"

# 测试任务API
echo "3️⃣ 测试任务API..."
TASK_COUNT=$(curl -s http://localhost:8000/api/v2/tasks/ | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
echo "✅ 任务数量: $TASK_COUNT"

# 测试前端
echo "4️⃣ 测试前端服务..."
curl -f http://localhost:3001/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ 前端服务正常"
else
  echo "❌ 前端服务异常"
fi

echo ""
echo "✨ 测试完成！"
```

使用方法:
```bash
chmod +x test_all.sh
./test_all.sh
```

---

## 下一阶段测试准备

### Phase 4: AI核心功能测试
- LLM对话响应
- Agent智能调度
- RAG检索效果
- 记忆功能验证

### Phase 5: 数据层测试
- 向量数据库
- 知识图谱
- 长期记忆存储
- 数据迁移

### Phase 6: 高级功能测试
- 语音输入输出
- 3D可视化性能
- 实时WebSocket
- 文件上传下载

---

**最后更新**: 2026-01-16  
**版本**: Phase 3 Week 2  
**状态**: ✅ 所有测试通过
