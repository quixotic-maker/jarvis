import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider, useToast } from './components/ToastProvider'
import ErrorBoundary from './components/ErrorBoundary'
import LoadingSpinner from './components/ui/LoadingSpinner'
import { setToastHandler } from './api/client'
import { useEffect, lazy, Suspense } from 'react'

// 懒加载页面组件 - 按需加载，减少初始包大小
const Chat = lazy(() => import('./pages/Chat'))
const ChatV2 = lazy(() => import('./pages/ChatV2'))
const ChatV3 = lazy(() => import('./pages/ChatV3'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Tasks = lazy(() => import('./pages/Tasks'))
const Schedules = lazy(() => import('./pages/Schedules'))
const Agents = lazy(() => import('./pages/Agents'))
const AgentsPage = lazy(() => import('./pages/AgentsPage'))
const MCPToolsPage = lazy(() => import('./pages/MCPToolsPage'))
const BrainPage = lazy(() => import('./pages/BrainPage'))
const SchedulePage = lazy(() => import('./pages/SchedulePage'))
const LearningPage = lazy(() => import('./pages/LearningPage'))
const GrowthPage = lazy(() => import('./pages/GrowthPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))

// 创建React Query客户端 - 优化缓存策略
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2, // 失败后重试2次
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // 指数退避
      refetchOnWindowFocus: false, // 窗口聚焦时不自动重新获取
      refetchOnReconnect: true, // 网络重连时重新获取
      staleTime: 5 * 60 * 1000, // 5分钟内数据视为新鲜
      cacheTime: 10 * 60 * 1000, // 10分钟后清除未使用的缓存
    },
  },
})

function AppRoutes() {
  const { error } = useToast()
  
  // 将Toast处理函数注入到API客户端
  useEffect(() => {
    setToastHandler(error)
  }, [error])
  
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={<LoadingSpinner fullScreen text="加载中..." />}>
          <Routes>
            {/* 默认重定向到新版对话页面 */}
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatV3 />} />
            <Route path="/chat-v2" element={<ChatV2 />} />
            <Route path="/chat-old" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/schedules" element={<Schedules />} />
            <Route path="/agents-old" element={<Agents />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/tools" element={<MCPToolsPage />} />
            <Route path="/brain" element={<BrainPage />} />
            <Route path="/schedule" element={<SchedulePage />} />
            <Route path="/learning" element={<LearningPage />} />
            <Route path="/growth" element={<GrowthPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AppRoutes />
      </ToastProvider>
    </QueryClientProvider>
  )
}

export default App
