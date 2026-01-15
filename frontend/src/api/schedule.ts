// 日程管理API服务
import api from './client'
import type {
  ApiResponse,
  PaginatedResponse,
  Schedule,
  ScheduleCreate,
  ScheduleUpdate
} from './types'

const API_PREFIX = '/v2/schedules'

export interface GetSchedulesParams {
  page?: number
  page_size?: number
  user_id?: string
  start_date?: string
  end_date?: string
  is_completed?: boolean
}

// 获取日程列表
export const getSchedules = async (params: GetSchedulesParams = {}): Promise<PaginatedResponse<Schedule>> => {
  const response = await api.get<PaginatedResponse<Schedule>>(API_PREFIX, { params })
  return response.data
}

// 获取单个日程
export const getSchedule = async (id: number): Promise<ApiResponse<Schedule>> => {
  const response = await api.get<ApiResponse<Schedule>>(`${API_PREFIX}/${id}`)
  return response.data
}

// 创建日程
export const createSchedule = async (
  data: ScheduleCreate,
  userId: string = 'default_user'
): Promise<ApiResponse<Schedule>> => {
  const response = await api.post<ApiResponse<Schedule>>(
    API_PREFIX,
    data,
    { params: { user_id: userId } }
  )
  return response.data
}

// 更新日程
export const updateSchedule = async (
  id: number,
  data: ScheduleUpdate
): Promise<ApiResponse<Schedule>> => {
  const response = await api.put<ApiResponse<Schedule>>(`${API_PREFIX}/${id}`, data)
  return response.data
}

// 删除日程
export const deleteSchedule = async (id: number): Promise<ApiResponse<null>> => {
  const response = await api.delete<ApiResponse<null>>(`${API_PREFIX}/${id}`)
  return response.data
}

// 标记日程完成
export const completeSchedule = async (id: number): Promise<ApiResponse<Schedule>> => {
  const response = await api.patch<ApiResponse<Schedule>>(`${API_PREFIX}/${id}/complete`)
  return response.data
}

// 取消日程完成
export const uncompleteSchedule = async (id: number): Promise<ApiResponse<Schedule>> => {
  const response = await api.patch<ApiResponse<Schedule>>(`${API_PREFIX}/${id}/uncomplete`)
  return response.data
}

export default {
  getSchedules,
  getSchedule,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  completeSchedule,
  uncompleteSchedule
}
