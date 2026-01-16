import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider, useToast } from './components/ToastProvider'
import ErrorBoundary from './components/ErrorBoundary'
import { setToastHandler } from './api/client'
import { useEffect } from 'react'
import Chat from './pages/Chat'
import ChatV2 from './pages/ChatV2'
import ChatV3 from './pages/ChatV3'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Schedules from './pages/Schedules'
import Agents from './pages/Agents'
import AgentsPage from './pages/AgentsPage'
import MCPToolsPage from './pages/MCPToolsPage'
import BrainPage from './pages/BrainPage'
import SchedulePage from './pages/SchedulePage'
import LearningPage from './pages/LearningPage'
import GrowthPage from './pages/GrowthPage'
import SettingsPage from './pages/SettingsPage'

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5分钟
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
