// 任务管理API服务
import api from './client'
import type {
  ApiResponse,
  PaginatedResponse,
  Task,
  TaskCreate,
  TaskUpdate
} from './types'

const API_PREFIX = '/v2/tasks'

export interface GetTasksParams {
  page?: number
  page_size?: number
  user_id?: string
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority?: 'low' | 'medium' | 'high'
  tag?: string
}

// 获取任务列表
export const getTasks = async (params: GetTasksParams = {}): Promise<PaginatedResponse<Task>> => {
  const response = await api.get<PaginatedResponse<Task>>(API_PREFIX, { params })
  return response.data
}

// 获取单个任务
export const getTask = async (id: number): Promise<ApiResponse<Task>> => {
  const response = await api.get<ApiResponse<Task>>(`${API_PREFIX}/${id}`)
  return response.data
}

// 创建任务
export const createTask = async (
  data: TaskCreate,
  userId: string = 'default_user'
): Promise<ApiResponse<Task>> => {
  const response = await api.post<ApiResponse<Task>>(
    API_PREFIX,
    data,
    { params: { user_id: userId } }
  )
  return response.data
}

// 更新任务
export const updateTask = async (id: number, data: TaskUpdate): Promise<ApiResponse<Task>> => {
  const response = await api.put<ApiResponse<Task>>(`${API_PREFIX}/${id}`, data)
  return response.data
}

// 删除任务
export const deleteTask = async (id: number): Promise<ApiResponse<null>> => {
  const response = await api.delete<ApiResponse<null>>(`${API_PREFIX}/${id}`)
  return response.data
}

// 标记任务完成
export const completeTask = async (id: number): Promise<ApiResponse<Task>> => {
  const response = await api.patch<ApiResponse<Task>>(`${API_PREFIX}/${id}/complete`)
  return response.data
}

// 更新任务进度
export const updateTaskProgress = async (
  id: number,
  progress: number
): Promise<ApiResponse<Task>> => {
  const response = await api.patch<ApiResponse<Task>>(
    `${API_PREFIX}/${id}/progress`,
    null,
    { params: { progress } }
  )
  return response.data
}

export default {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  completeTask,
  updateTaskProgress
}
