// API类型定义
export interface ApiResponse<T = any> {
  status: 'success' | 'error' | 'warning'
  message: string
  data?: T
  timestamp: string
}

export interface PaginatedResponse<T> {
  status: 'success' | 'error' | 'warning'
  message: string
  data: T[]
  meta: PaginationMeta
  timestamp: string
}

export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
}

// ==================== 日程相关类型 ====================

export interface Schedule {
  id: number
  user_id: string
  title: string
  description?: string | null
  start_time: string
  end_time?: string | null
  location?: string | null
  attendees?: string[] | null
  priority: 'low' | 'medium' | 'high'
  event_type: 'meeting' | 'task' | 'reminder' | 'event'
  is_completed: boolean
  created_at: string
  updated_at?: string | null
}

export interface ScheduleCreate {
  title: string
  description?: string
  start_time: string
  end_time?: string
  location?: string
  attendees?: string[]
  priority?: 'low' | 'medium' | 'high'
  event_type?: 'meeting' | 'task' | 'reminder' | 'event'
}

export interface ScheduleUpdate {
  title?: string
  description?: string
  start_time?: string
  end_time?: string
  location?: string
  attendees?: string[]
  priority?: 'low' | 'medium' | 'high'
  event_type?: 'meeting' | 'task' | 'reminder' | 'event'
  is_completed?: boolean
}

// ==================== 任务相关类型 ====================

export interface Task {
  id: number
  user_id: string
  title: string
  description?: string | null
  priority: 'low' | 'medium' | 'high'
  due_date?: string | null
  tags?: string[]
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  progress: number
  created_at: string
  updated_at?: string | null
  completed_at?: string | null
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
  due_date?: string
  tags?: string[]
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
  due_date?: string
  tags?: string[]
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled'
}

// ==================== 学习相关类型 ====================

export interface LearningPlan {
  id: number
  user_id: string
  title: string
  description?: string
  target: string
  due_date?: string
  tags?: string[]
  progress: number
  status: 'active' | 'paused' | 'completed' | 'cancelled'
  tasks_total: number
  tasks_completed: number
  created_at: string
  updated_at?: string
}

export interface LearningResource {
  id: number
  user_id: string
  title: string
  resource_type: 'video' | 'article' | 'book' | 'course' | 'doc'
  url?: string
  description?: string
  tags?: string[]
  progress: number
  created_at: string
  updated_at?: string
}

// ==================== 知识图谱类型 ====================

export interface KnowledgeNode {
  id: number
  user_id: string
  title: string
  node_type: 'concept' | 'skill' | 'project' | 'resource' | 'person'
  description?: string
  tags?: string[]
  connections: number
  created_at: string
  updated_at?: string
}

// ==================== 设置相关类型 ====================

export interface SystemPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US' | 'ja-JP'
  font_size: 'small' | 'medium' | 'large'
  sound_enabled: boolean
  notifications_enabled: boolean
  auto_save: boolean
}

export interface AgentPreferences {
  default_agent: string
  response_speed: 'fast' | 'balanced' | 'quality'
  creativity: number
  max_tokens: number
  temperature: number
  enable_voice: boolean
  enable_memory: boolean
}

export interface UserSettings {
  system: SystemPreferences
  agent: AgentPreferences
}

export interface SettingsResponse {
  user_id: string
  settings: UserSettings
  updated_at: string
}

// ==================== 对话相关类型 ====================

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  session_id?: string
  user_id?: string
  stream?: boolean
}

export interface ChatResponse {
  session_id: string
  message_id: number
  content: string
  intent?: string
  intent_confidence?: number
  agent_used?: string
  action_result?: any
  suggestions?: string[]
  response_time_ms: number
}

// ==================== Agent相关类型 ====================

export interface AgentInfo {
  name: string
  display_name: string
  description: string
  category: string
  capabilities: string[]
  status: string
}

export interface AgentStats {
  total_calls: number
  success_rate: number
  avg_response_time_ms: number
  last_used?: string
}

export interface AgentDetail {
  info: AgentInfo
  stats: AgentStats
}
