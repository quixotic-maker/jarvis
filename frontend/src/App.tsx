import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Schedules from './pages/Schedules'
import Agents from './pages/Agents'

function App() {
  return (
    <Router>
      <Routes>
        {/* 默认重定向到对话页面 */}
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/schedules" element={<Schedules />} />
        <Route path="/agents" element={<Agents />} />
      </Routes>
    </Router>
  )
}

export default App
