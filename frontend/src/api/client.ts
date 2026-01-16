import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

// ==================== 类型定义 ====================

export interface Task {
  id: number
  user_input: string
  task_type: string
  status: string
  assigned_agent: string | null
  result: any
  created_at: string
}

export interface Schedule {
  id: number
  title: string
  description: string | null
  start_time: string
  end_time: string | null
  location: string | null
  is_completed: boolean
}

export interface Agent {
  name: string
  description: string
}

export interface AgentLog {
  id: number
  agent_name: string
  task_id: number | null
  action: string
  execution_time: number
  status: string
  created_at: string
}

// 对话相关类型
export interface ChatMessage {
  id: number
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  intent?: string
  agent_used?: string
  emotion?: string
  created_at: string
}

export interface ChatSession {
  id: string
  user_id: string
  title: string | null
  summary: string | null
  is_active: boolean
  message_count: number
  last_activity: string
  created_at: string
}

export interface ChatResponse {
  session_id: string
  message_id: number
  content: string
  intent: string
  intent_confidence: number
  agent_used?: string
  action_result?: any
  suggestions?: string[]
  emotion_detected?: string
  response_time_ms: number
}

// ==================== 对话 API ====================

export const chatAPI = {
  // 发送消息
  send: (message: string, sessionId?: string, userId: string = 'default_user') =>
    api.post<ChatResponse>('/chat/chat', { message, session_id: sessionId, user_id: userId }),

  // 快速对话
  quickChat: (message: string, userId: string = 'default_user') =>
    api.post('/chat/chat/quick', null, { params: { message, user_id: userId } }),

  // 获取会话列表
  getSessions: (userId: string = 'default_user', limit: number = 20) =>
    api.get<ChatSession[]>('/chat/sessions', { params: { user_id: userId, limit } }),

  // 创建新会话
  createSession: (userId: string = 'default_user') =>
    api.post<ChatSession>('/chat/sessions', null, { params: { user_id: userId } }),

  // 获取会话消息
  getMessages: (sessionId: string, limit: number = 50) =>
    api.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`, { params: { limit } }),

  // 删除会话
  deleteSession: (sessionId: string) =>
    api.delete(`/chat/sessions/${sessionId}`),
}

// ==================== 用户档案 API ====================

export const profileAPI = {
  get: (userId: string = 'default_user') =>
    api.get('/chat/profile', { params: { user_id: userId } }),

  update: (updates: Record<string, any>, userId: string = 'default_user') =>
    api.put('/chat/profile', updates, { params: { user_id: userId } }),
}

// ==================== 记忆 API ====================

export const memoryAPI = {
  search: (query?: string, memoryType?: string, userId: string = 'default_user') =>
    api.get('/chat/memories', { params: { query, memory_type: memoryType, user_id: userId } }),

  add: (content: string, memoryType: string = 'episode', userId: string = 'default_user') =>
    api.post('/chat/memories', { content, memory_type: memoryType }, { params: { user_id: userId } }),
}

// ==================== 关系 API ====================

export const relationshipAPI = {
  list: (userId: string = 'default_user', relationshipType?: string) =>
    api.get('/chat/relationships', { params: { user_id: userId, relationship_type: relationshipType } }),

  add: (data: {
    person_name: string
    relationship_type: string
    phone?: string
    email?: string
    company?: string
    notes?: string
  }, userId: string = 'default_user') =>
    api.post('/chat/relationships', data, { params: { user_id: userId } }),
}

// ==================== 偏好 API ====================

export const preferenceAPI = {
  getAll: (userId: string = 'default_user') =>
    api.get('/chat/preferences', { params: { user_id: userId } }),

  set: (category: string, key: string, value: any, userId: string = 'default_user') =>
    api.put(`/chat/preferences/${category}/${key}`, value, { params: { user_id: userId } }),
}

// ==================== 原有 API ====================

export const taskAPI = {
  create: (user_input: string) => api.post<Task>('/tasks/', { user_input }),
  list: () => api.get<Task[]>('/tasks/'),
  get: (id: number) => api.get<Task>(`/tasks/${id}`),
}

export const scheduleAPI = {
  list: () => api.get<Schedule[]>('/schedules/'),
  get: (id: number) => api.get<Schedule>(`/schedules/${id}`),
  complete: (id: number) => api.patch(`/schedules/${id}/complete`),
}

export const agentAPI = {
  list: () => api.get<Agent[]>('/agents/'),
  logs: () => api.get<AgentLog[]>('/agents/logs'),
  logsByName: (name: string) => api.get<AgentLog[]>(`/agents/${name}/logs`),
  process: (agentName: string, input: string) =>
    api.post(`/agents/${agentName}/process`, { input }),
}
// ==================== 学习工作台 API ====================

export interface LearningPlan {
  id: number
  user_id: string
  title: string
  goal: string
  duration_days: number
  progress: number
  status: 'active' | 'paused' | 'completed'
  tasks_count: number
  completed_tasks_count: number
  start_date: string
  end_date: string | null
  tags: string[]
  created_at: string
}

export interface DailyTask {
  id: number
  plan_id: number
  task_date: string
  title: string
  description: string | null
  task_type: 'reading' | 'practice' | 'review' | 'project'
  estimated_duration: number | null
  actual_duration: number | null
  completed: boolean
  feedback: string | null
  created_at: string
  completed_at: string | null
}

export interface BaseResponse<T> {
  success: boolean
  data?: T
  message?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  total: number
  page: number
  page_size: number
}

export const learningAPI = {
  // 学习计划
  plans: {
    list: (userId: string = 'default_user', status?: string, skip: number = 0, limit: number = 20) =>
      api.get<PaginatedResponse<LearningPlan>>('/v2/learning/plans', {
        params: { user_id: userId, status, skip, limit }
      }),
    
    get: (planId: number) =>
      api.get<BaseResponse<LearningPlan>>(`/v2/learning/plans/${planId}`),
    
    create: (data: {
      title: string
      goal: string
      duration_days?: number
      tags?: string[]
    }, userId: string = 'default_user') =>
      api.post<BaseResponse<LearningPlan>>('/v2/learning/plans', data, {
        params: { user_id: userId }
      }),
    
    update: (planId: number, data: {
      title?: string
      goal?: string
      status?: string
    }) =>
      api.put<BaseResponse<LearningPlan>>(`/v2/learning/plans/${planId}`, data),
    
    delete: (planId: number) =>
      api.delete<BaseResponse<null>>(`/v2/learning/plans/${planId}`),
  },

  // 每日任务
  tasks: {
    today: (userId: string = 'default_user') =>
      api.get<BaseResponse<DailyTask[]>>('/v2/learning/tasks/today', {
        params: { user_id: userId }
      }),
    
    byPlan: (planId: number, skip: number = 0, limit: number = 50) =>
      api.get<PaginatedResponse<DailyTask>>(`/v2/learning/plans/${planId}/tasks`, {
        params: { skip, limit }
      }),
    
    create: (data: {
      plan_id: number
      task_date: string
      title: string
      description?: string
      task_type?: string
      estimated_duration?: number
    }) =>
      api.post<BaseResponse<DailyTask>>('/v2/learning/tasks', data),
    
    update: (taskId: number, data: {
      title?: string
      description?: string
      completed?: boolean
      actual_duration?: number
      feedback?: string
    }) =>
      api.put<BaseResponse<DailyTask>>(`/v2/learning/tasks/${taskId}`, data),
    
    delete: (taskId: number) =>
      api.delete<BaseResponse<null>>(`/v2/learning/tasks/${taskId}`),
  },
}
// ==================== 知识大脑 API ====================

export interface KnowledgeNode {
  id: number
  user_id: string
  label: string
  node_type: 'concept' | 'skill' | 'project' | 'resource' | 'person'
  description: string | null
  tags: string[]
  metadata: Record<string, any> | null
  connections_count: number
  created_at: string
  updated_at: string
}

export interface Connection {
  id: number
  from_node_id: number
  to_node_id: number
  relation_type: string
  weight: number
  description: string | null
  created_at: string
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[]
  edges: Connection[]
  stats: {
    total_nodes: number
    total_connections: number
    node_types: Record<string, number>
    avg_connections: number
  }
}

export const knowledgeAPI = {
  // 知识节点
  nodes: {
    list: (userId: string = 'default_user', nodeType?: string, search?: string, skip: number = 0, limit: number = 50) =>
      api.get<PaginatedResponse<KnowledgeNode>>('/v2/knowledge/nodes', {
        params: { user_id: userId, node_type: nodeType, search, skip, limit }
      }),
    
    get: (nodeId: number) =>
      api.get<BaseResponse<KnowledgeNode>>(`/v2/knowledge/nodes/${nodeId}`),
    
    create: (data: {
      label: string
      node_type: string
      description?: string
      tags?: string[]
      metadata?: Record<string, any>
    }, userId: string = 'default_user') =>
      api.post<BaseResponse<KnowledgeNode>>('/v2/knowledge/nodes', data, {
        params: { user_id: userId }
      }),
    
    update: (nodeId: number, data: {
      label?: string
      description?: string
      tags?: string[]
      metadata?: Record<string, any>
    }) =>
      api.put<BaseResponse<KnowledgeNode>>(`/v2/knowledge/nodes/${nodeId}`, data),
    
    delete: (nodeId: number) =>
      api.delete<BaseResponse<null>>(`/v2/knowledge/nodes/${nodeId}`),
  },

  // 知识连接
  connections: {
    list: (nodeId?: number, skip: number = 0, limit: number = 100) =>
      api.get<PaginatedResponse<Connection>>('/v2/knowledge/connections', {
        params: { node_id: nodeId, skip, limit }
      }),
    
    create: (data: {
      from_node_id: number
      to_node_id: number
      relation_type: string
      weight?: number
      description?: string
    }) =>
      api.post<BaseResponse<Connection>>('/v2/knowledge/connections', data),
    
    delete: (connectionId: number) =>
      api.delete<BaseResponse<null>>(`/v2/knowledge/connections/${connectionId}`),
  },

  // 知识图谱
  graph: (userId: string = 'default_user', centerNodeId?: number, depth: number = 2) =>
    api.get<BaseResponse<KnowledgeGraph>>('/v2/knowledge/graph', {
      params: { user_id: userId, center_node_id: centerNodeId, depth }
    }),

  // 搜索
  search: (query: string, userId: string = 'default_user') =>
    api.get<BaseResponse<KnowledgeNode[]>>('/v2/knowledge/search', {
      params: { query, user_id: userId }
    }),
}

// ==================== Agents管理 API ====================

export interface AgentInfo {
  id: string
  name: string
  description: string
  category: string
  category_label: string
  status: 'idle' | 'busy' | 'error'
  last_active: string
  capabilities: string[]
  total_executions: number
  success_rate: number
  avg_response_time: number
}

export interface AgentExecution {
  id: number
  agent_name: string
  task_type: string
  input_data: Record<string, any>
  output_data: Record<string, any> | null
  status: 'success' | 'failed' | 'running'
  execution_time: number
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export interface AgentStats {
  total_agents: number
  active_agents: number
  total_executions: number
  success_rate: number
  avg_response_time: number
  executions_by_category: Record<string, number>
  executions_today: number
}

export const agentsAPI = {
  list: (category?: string, status?: string, search?: string) =>
    api.get<BaseResponse<AgentInfo[]>>('/v2/agents/list', {
      params: { category, status, search }
    }),
  
  get: (agentId: string) =>
    api.get<BaseResponse<AgentInfo>>(`/v2/agents/${agentId}`),
  
  executions: (agentName: string, skip: number = 0, limit: number = 20) =>
    api.get<PaginatedResponse<AgentExecution>>(`/v2/agents/${agentName}/executions`, {
      params: { skip, limit }
    }),
  
  stats: () =>
    api.get<BaseResponse<AgentStats>>('/v2/agents/stats/overview'),
}

// ==================== 成长追踪 API ====================

export interface DailyStats {
  date: string
  tasks_completed: number
  study_minutes: number
  agents_used: number
  knowledge_added: number
}

export interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  category: string
  progress: number
  total: number
  current: number
  unlocked: boolean
  unlocked_at: string | null
}

export interface GrowthOverview {
  total_days: number
  total_tasks: number
  total_study_hours: number
  total_knowledge_nodes: number
  achievements_unlocked: number
  current_streak: number
  longest_streak: number
  level: number
  level_progress: number
}

export interface ActivityHeatmap {
  date: string
  activity_count: number
  intensity: 'none' | 'low' | 'medium' | 'high'
}

export const growthAPI = {
  overview: (userId: string = 'default_user') =>
    api.get<BaseResponse<GrowthOverview>>('/v2/growth/overview', {
      params: { user_id: userId }
    }),
  
  dailyStats: (userId: string = 'default_user', startDate?: string, endDate?: string) =>
    api.get<BaseResponse<DailyStats[]>>('/v2/growth/daily-stats', {
      params: { user_id: userId, start_date: startDate, end_date: endDate }
    }),
  
  achievements: (userId: string = 'default_user', category?: string, unlockedOnly: boolean = false) =>
    api.get<BaseResponse<Achievement[]>>('/v2/growth/achievements', {
      params: { user_id: userId, category, unlocked_only: unlockedOnly }
    }),
  
  activityHeatmap: (userId: string = 'default_user', year: number = 2026) =>
    api.get<BaseResponse<ActivityHeatmap[]>>('/v2/growth/activity-heatmap', {
      params: { user_id: userId, year }
    }),
  
  streak: (userId: string = 'default_user') =>
    api.get<BaseResponse<any>>('/v2/growth/streak', {
      params: { user_id: userId }
    }),
  
  checkIn: (userId: string = 'default_user') =>
    api.post<BaseResponse<any>>('/v2/growth/check-in', null, {
      params: { user_id: userId }
    }),
}
