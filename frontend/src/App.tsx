import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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

function App() {
  return (
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
  )
}

export default App
