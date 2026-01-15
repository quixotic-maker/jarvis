// 用户设置API服务
import api from './client'
import type {
  ApiResponse,
  UserSettings,
  SettingsResponse,
  SystemPreferences,
  AgentPreferences
} from './types'

const API_PREFIX = '/v2/settings'

// 获取用户设置
export const getSettings = async (userId: string = 'default_user'): Promise<ApiResponse<SettingsResponse>> => {
  const response = await api.get<ApiResponse<SettingsResponse>>(
    API_PREFIX,
    { params: { user_id: userId } }
  )
  return response.data
}

// 更新所有设置
export const updateSettings = async (
  data: UserSettings,
  userId: string = 'default_user'
): Promise<ApiResponse<SettingsResponse>> => {
  const response = await api.put<ApiResponse<SettingsResponse>>(
    API_PREFIX,
    data,
    { params: { user_id: userId } }
  )
  return response.data
}

// 更新系统偏好
export const updateSystemPreferences = async (
  data: SystemPreferences,
  userId: string = 'default_user'
): Promise<ApiResponse<SettingsResponse>> => {
  const response = await api.patch<ApiResponse<SettingsResponse>>(
    `${API_PREFIX}/system`,
    data,
    { params: { user_id: userId } }
  )
  return response.data
}

// 更新Agent配置
export const updateAgentPreferences = async (
  data: AgentPreferences,
  userId: string = 'default_user'
): Promise<ApiResponse<SettingsResponse>> => {
  const response = await api.patch<ApiResponse<SettingsResponse>>(
    `${API_PREFIX}/agent`,
    data,
    { params: { user_id: userId } }
  )
  return response.data
}

// 重置为默认设置
export const resetSettings = async (
  userId: string = 'default_user'
): Promise<ApiResponse<SettingsResponse>> => {
  const response = await api.post<ApiResponse<SettingsResponse>>(
    `${API_PREFIX}/reset`,
    null,
    { params: { user_id: userId } }
  )
  return response.data
}

export default {
  getSettings,
  updateSettings,
  updateSystemPreferences,
  updateAgentPreferences,
  resetSettings
}
