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
