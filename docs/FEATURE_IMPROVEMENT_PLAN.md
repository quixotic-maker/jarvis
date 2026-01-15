# Jarvis 功能改进计划

## 📌 当前状态分析

### ✅ 已完成部分
- **Phase 1-2**: 前端UI框架和页面布局（纯展示）
- **Phase 3 Week 1**: 后端API基础架构（CRUD接口）
- **Phase 3 Week 2**: 前后端简单集成（日程、设置页面）

### ❌ 待实现功能
- **Agent智能调度系统**：未实现
- **多Agent协作机制**：未实现
- **对话交互逻辑**：未实现
- **LLM集成**：未实现
- **任务自动生成**：未实现

---

## 🐛 问题1: 对话框点不了

### 当前问题
ChatV3页面的Agent卡片点击没有实际交互逻辑，只是调用了`handleQuickAction`。

### 解决方案

**1. 添加Agent选择状态管理**
```typescript
// 在ChatV3.tsx中添加
const [selectedAgents, setSelectedAgents] = useState<string[]>([])

// Agent点击处理
const handleAgentClick = (agentId: string) => {
  setSelectedAgents(prev => {
    if (prev.includes(agentId)) {
      // 再次点击取消选择
      return prev.filter(id => id !== agentId)
    } else {
      // 添加到选择列表
      return [...prev, agentId]
    }
  })
}
```

**2. 修改Agent卡片渲染**
```tsx
{featuredAgents.map((agent) => (
  <div
    key={agent.id}
    onClick={() => handleAgentClick(agent.id)}
    className={`
      cursor-pointer transition-all
      ${selectedAgents.includes(agent.id) 
        ? 'ring-2 ring-emerald-500 bg-emerald-500/10' 
        : 'hover:bg-slate-800/50'}
    `}
  >
    <AgentCard {...agent} />
    {selectedAgents.includes(agent.id) && (
      <Badge variant="success" className="absolute top-2 right-2">
        已选择
      </Badge>
    )}
  </div>
))}
```

**3. 发送消息时携带选择的Agent**
```typescript
const sendMessage = async (content: string) => {
  const payload = {
    message: content,
    selected_agents: selectedAgents, // 用户手动选择的Agent
    allow_auto_routing: true, // 允许主Agent自动调度
  }
  
  await chatAPI.sendMessage(payload)
}
```

---

## 🤝 问题2: 多Agent协作机制设计

### 架构设计

```
┌─────────────────────────────────────────────────┐
│              用户输入                            │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│         Coordinator (主Agent)                    │
│  - 分析意图                                      │
│  - 决策是否需要调用其他Agent                     │
│  - 生成子任务提示词                              │
│  - 汇总结果                                      │
└───────────┬──────────────┬──────────────────────┘
            │              │
    ┌───────┴──────┐   ┌──┴────────┐
    │              │   │           │
    ▼              ▼   ▼           ▼
┌─────────┐  ┌──────────┐  ┌─────────┐
│Schedule │  │CodeAgent │  │Weather  │
│Agent    │  │          │  │Agent    │
└─────────┘  └──────────┘  └─────────┘
    │              │           │
    └──────┬───────┴───────────┘
           │
           ▼
    ┌─────────────┐
    │   任务队列   │
    │  (并发处理) │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  结果汇总   │
    └─────────────┘
           │
           ▼
      返回用户
```

### 数据模型

**1. Agent实例表**
```sql
CREATE TABLE agent_instances (
    id INTEGER PRIMARY KEY,
    agent_type VARCHAR(50),      -- 'ScheduleAgent', 'CodeAgent'等
    instance_id VARCHAR(100),     -- 'schedule_001', 'schedule_002'
    status VARCHAR(20),           -- 'idle', 'busy', 'error'
    current_task_id INTEGER,
    created_at TIMESTAMP,
    last_active TIMESTAMP
);
```

**2. Agent任务队列**
```sql
CREATE TABLE agent_tasks (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER,
    parent_task_id INTEGER,      -- 父任务ID（如果是子任务）
    agent_type VARCHAR(50),
    agent_instance_id VARCHAR(100),
    prompt TEXT,                  -- 给Agent的提示词
    context JSON,                 -- 上下文信息
    rules JSON,                   -- 规则和限制
    status VARCHAR(20),           -- 'pending', 'processing', 'completed', 'failed'
    result JSON,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**3. Agent配置表**
```sql
CREATE TABLE agent_configs (
    agent_type VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100),
    description TEXT,
    system_prompt TEXT,          -- Agent的系统提示词
    roles JSON,                  -- ["规划师", "执行者"]
    rules JSON,                  -- 行为规则
    max_instances INTEGER,       -- 最大实例数
    enabled BOOLEAN
);
```

### 后端实现逻辑

```python
# backend/app/services/agent_orchestrator.py

class AgentOrchestrator:
    """Agent编排器 - 主控Agent"""
    
    async def process_message(
        self, 
        user_message: str,
        selected_agents: List[str] = None,
        conversation_id: int = None
    ):
        """处理用户消息"""
        
        # 1. 分析意图
        intent = await self.analyze_intent(user_message)
        
        # 2. 决策需要哪些Agent
        if selected_agents:
            # 用户手动选择了Agent
            required_agents = selected_agents
        else:
            # 主Agent自动决策
            required_agents = await self.decide_agents(intent, user_message)
        
        # 3. 生成子任务
        tasks = []
        for agent_type in required_agents:
            task = await self.create_agent_task(
                agent_type=agent_type,
                user_message=user_message,
                intent=intent,
                conversation_id=conversation_id
            )
            tasks.append(task)
        
        # 4. 并发执行任务
        results = await asyncio.gather(
            *[self.execute_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # 5. 汇总结果
        final_response = await self.synthesize_results(
            user_message=user_message,
            agent_results=results
        )
        
        return final_response
    
    async def create_agent_task(
        self,
        agent_type: str,
        user_message: str,
        intent: dict,
        conversation_id: int
    ):
        """创建Agent任务"""
        
        # 获取Agent配置
        config = await self.get_agent_config(agent_type)
        
        # 分配或创建实例
        instance = await self.allocate_instance(agent_type)
        
        # 生成针对该Agent的提示词
        prompt = await self.generate_agent_prompt(
            agent_type=agent_type,
            user_message=user_message,
            intent=intent,
            system_prompt=config.system_prompt,
            roles=config.roles,
            rules=config.rules
        )
        
        # 创建任务记录
        task = AgentTask(
            agent_type=agent_type,
            agent_instance_id=instance.id,
            prompt=prompt,
            context={
                "user_message": user_message,
                "intent": intent,
                "roles": config.roles,
                "rules": config.rules
            },
            status="pending"
        )
        
        db.add(task)
        await db.commit()
        
        return task
    
    async def allocate_instance(self, agent_type: str):
        """分配Agent实例（支持一个Agent多个实例）"""
        
        # 查找空闲实例
        idle_instance = await db.query(AgentInstance).filter(
            AgentInstance.agent_type == agent_type,
            AgentInstance.status == 'idle'
        ).first()
        
        if idle_instance:
            idle_instance.status = 'busy'
            await db.commit()
            return idle_instance
        
        # 检查是否可以创建新实例
        config = await self.get_agent_config(agent_type)
        current_count = await db.query(AgentInstance).filter(
            AgentInstance.agent_type == agent_type
        ).count()
        
        if current_count < config.max_instances:
            # 创建新实例
            new_instance = AgentInstance(
                agent_type=agent_type,
                instance_id=f"{agent_type}_{current_count + 1}",
                status='busy'
            )
            db.add(new_instance)
            await db.commit()
            return new_instance
        
        # 等待实例释放
        return await self.wait_for_instance(agent_type)
    
    async def execute_task(self, task: AgentTask):
        """执行Agent任务"""
        
        try:
            task.status = 'processing'
            await db.commit()
            
            # 调用LLM执行任务
            result = await self.call_llm(
                prompt=task.prompt,
                context=task.context
            )
            
            task.status = 'completed'
            task.result = result
            task.completed_at = datetime.now()
            
            # 释放实例
            instance = await db.query(AgentInstance).filter(
                AgentInstance.instance_id == task.agent_instance_id
            ).first()
            instance.status = 'idle'
            instance.current_task_id = None
            
            await db.commit()
            
            return {
                'agent_type': task.agent_type,
                'instance': task.agent_instance_id,
                'result': result,
                'success': True
            }
            
        except Exception as e:
            task.status = 'failed'
            task.result = {'error': str(e)}
            await db.commit()
            
            return {
                'agent_type': task.agent_type,
                'error': str(e),
                'success': False
            }
```

---

## 💡 问题3: Agent状态显示

### 问题分析
"已完成"状态不应显示在前端Agent列表，而应该显示在：
1. **对话气泡中** - 标注哪些Agent参与了回答
2. **任务历史中** - 显示Agent调用链路

### 解决方案

**1. 对话消息中显示Agent参与情况**
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agents_used?: Array<{
    agent_type: string
    agent_instance: string
    task_id: number
    result_summary: string
  }>
  created_at: string
}
```

**2. 前端展示**
```tsx
{message.agents_used && (
  <div className="mt-2 space-y-1">
    <p className="text-xs text-slate-500">参与Agent:</p>
    {message.agents_used.map(agent => (
      <Badge key={agent.task_id} variant="outline" size="sm">
        {agent.agent_type} ({agent.agent_instance})
      </Badge>
    ))}
  </div>
)}
```

**3. Agent列表只显示实时状态**
```tsx
<AgentCard
  name={agent.name}
  status={agent.current_status} // 'idle', 'busy'
  activeInstances={agent.instance_count} // "2/5" (当前/最大)
  lastUsed="2分钟前"
/>
```

---

## 🎯 问题4: 功能交互实现状态

### 实话实说：目前状态

✅ **已实现**:
- 前端UI框架
- 后端API基础CRUD
- 日程/设置数据的读写

❌ **未实现** (重要!):
- ❌ LLM对话功能
- ❌ Agent智能调度
- ❌ 多Agent协作
- ❌ 任务自动生成
- ❌ 实时消息流式输出
- ❌ WebSocket实时通信
- ❌ 语音输入输出
- ❌ 知识图谱可视化
- ❌ RAG检索增强

### 需要完成的核心功能

**Phase 3 Week 3-4 (即将开始)**:
1. LLM集成 (OpenAI/Claude API)
2. Agent编排器实现
3. WebSocket实时通信
4. 流式输出

**Phase 4** (AI核心):
1. 多Agent协作机制
2. RAG检索系统
3. 长期记忆管理
4. 智能决策引擎

---

## 📚 问题5: 学习工作台 - 每日任务生成

### 设计方案

**1. 数据模型**
```sql
-- 学习计划表
CREATE TABLE learning_plans (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(100),
    title VARCHAR(200),
    goal TEXT,                    -- 学习目标
    duration_days INTEGER,        -- 计划天数
    agent_generated BOOLEAN,      -- 是否由Agent生成
    status VARCHAR(20),
    created_at TIMESTAMP
);

-- 每日任务表
CREATE TABLE daily_tasks (
    id INTEGER PRIMARY KEY,
    plan_id INTEGER,
    task_date DATE,
    title VARCHAR(200),
    description TEXT,
    task_type VARCHAR(50),       -- 'reading', 'practice', 'review', 'project'
    estimated_duration INTEGER,  -- 预计时长(分钟)
    resources JSON,              -- 学习资源链接
    agent_generated BOOLEAN,
    completed BOOLEAN,
    completion_time INTEGER,     -- 实际花费时长
    feedback TEXT,               -- 完成后的反馈
    created_at TIMESTAMP
);
```

**2. Agent自动生成任务逻辑**
```python
# backend/app/services/learning_agent.py

class LearningAgent:
    """学习Agent - 负责生成学习计划和每日任务"""
    
    async def generate_learning_plan(
        self,
        user_id: str,
        learning_goal: str,
        duration_days: int,
        user_level: str = "beginner"
    ):
        """生成学习计划"""
        
        # 1. 分析学习目标
        prompt = f"""
        作为一个专业的学习规划师，请为用户制定一个{duration_days}天的学习计划。
        
        学习目标: {learning_goal}
        用户水平: {user_level}
        
        请输出：
        1. 学习路径规划（分阶段）
        2. 每个阶段的重点内容
        3. 推荐的学习资源
        4. 每日任务建议
        
        输出格式：JSON
        """
        
        plan_structure = await self.call_llm(prompt)
        
        # 2. 创建学习计划记录
        plan = LearningPlan(
            user_id=user_id,
            title=f"{learning_goal}学习计划",
            goal=learning_goal,
            duration_days=duration_days,
            agent_generated=True,
            status='active'
        )
        db.add(plan)
        await db.commit()
        
        # 3. 生成每日任务
        await self.generate_daily_tasks(plan, plan_structure)
        
        return plan
    
    async def generate_daily_tasks(
        self,
        plan: LearningPlan,
        plan_structure: dict
    ):
        """为学习计划生成每日任务"""
        
        start_date = date.today()
        
        for day in range(plan.duration_days):
            task_date = start_date + timedelta(days=day)
            
            # 根据计划结构生成当天任务
            prompt = f"""
            第{day + 1}天学习任务生成：
            
            学习目标: {plan.goal}
            当前阶段: {plan_structure['phases'][day // 7]['name']}
            
            请生成2-4个具体的学习任务，包括：
            1. 任务标题
            2. 详细描述
            3. 任务类型（阅读/练习/复习/项目）
            4. 预计时长
            5. 推荐资源
            
            输出格式：JSON数组
            """
            
            tasks = await self.call_llm(prompt)
            
            # 保存任务
            for task_data in tasks:
                task = DailyTask(
                    plan_id=plan.id,
                    task_date=task_date,
                    title=task_data['title'],
                    description=task_data['description'],
                    task_type=task_data['type'],
                    estimated_duration=task_data['duration'],
                    resources=task_data['resources'],
                    agent_generated=True,
                    completed=False
                )
                db.add(task)
            
        await db.commit()
    
    async def get_today_tasks(self, user_id: str):
        """获取今日学习任务"""
        
        today = date.today()
        
        tasks = await db.query(DailyTask).join(LearningPlan).filter(
            LearningPlan.user_id == user_id,
            DailyTask.task_date == today,
            LearningPlan.status == 'active'
        ).all()
        
        return tasks
```

**3. 前端学习工作台展示**
```tsx
// LearningPage.tsx

export default function LearningPage() {
  const [todayTasks, setTodayTasks] = useState<DailyTask[]>([])
  const [activePlans, setActivePlans] = useState<LearningPlan[]>([])
  
  useEffect(() => {
    loadTodayTasks()
    loadActivePlans()
  }, [])
  
  const loadTodayTasks = async () => {
    const response = await learningApi.getTodayTasks('default_user')
    setTodayTasks(response.data.data)
  }
  
  return (
    <MainLayout title="学习工作台">
      {/* 今日任务区域 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">今日学习任务</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {todayTasks.map(task => (
            <Card key={task.id} className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">{task.title}</h3>
                  <p className="text-sm text-slate-400 mb-3">
                    {task.description}
                  </p>
                  
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <Badge>{task.task_type}</Badge>
                    <span>⏱️ {task.estimated_duration}分钟</span>
                    {task.agent_generated && (
                      <Badge variant="outline">🤖 AI生成</Badge>
                    )}
                  </div>
                  
                  {/* 学习资源 */}
                  {task.resources && task.resources.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs text-slate-500 mb-1">推荐资源:</p>
                      {task.resources.map((resource, idx) => (
                        <a
                          key={idx}
                          href={resource.url}
                          className="block text-xs text-blue-400 hover:underline"
                        >
                          📄 {resource.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
                
                <Button
                  size="sm"
                  variant={task.completed ? 'success' : 'primary'}
                  onClick={() => toggleTaskComplete(task.id)}
                >
                  {task.completed ? '✓ 已完成' : '开始学习'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </section>
      
      {/* 学习计划列表 */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">我的学习计划</h2>
          <Button onClick={() => setShowCreatePlan(true)}>
            创建新计划
          </Button>
        </div>
        
        {/* 计划列表... */}
      </section>
    </MainLayout>
  )
}
```

---

## 🛠️ 实施路线图

### 近期 (Phase 3 Week 3-4)
1. **对话功能修复**
   - [ ] Agent选择交互
   - [ ] 多Agent选择状态
   - [ ] 发送消息携带Agent列表

2. **LLM集成**
   - [ ] OpenAI API接入
   - [ ] 流式输出实现
   - [ ] WebSocket通信

3. **基础Agent编排**
   - [ ] Coordinator实现
   - [ ] 单Agent调用
   - [ ] 结果返回

### 中期 (Phase 4)
1. **多Agent协作**
   - [ ] Agent实例管理
   - [ ] 任务队列系统
   - [ ] 并发执行
   - [ ] 结果汇总

2. **学习任务生成**
   - [ ] LearningAgent实现
   - [ ] 每日任务生成
   - [ ] 任务完成追踪

### 远期 (Phase 5-6)
1. **高级功能**
   - [ ] RAG检索
   - [ ] 知识图谱
   - [ ] 语音交互
   - [ ] 3D可视化

---

## 📝 下一步行动

### 立即修复（本次会话）
1. 修复对话框Agent点击交互
2. 添加Agent选择状态管理
3. 更新测试文档

### 下次开发（Phase 3 Week 3）
1. 集成OpenAI/Claude API
2. 实现基础Agent编排器
3. 完成流式对话输出

---

**最后更新**: 2026-01-16  
**当前阶段**: Phase 3 Week 2 完成  
**下一阶段**: Phase 3 Week 3 - AI核心集成
