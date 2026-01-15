import { Link, useLocation } from 'react-router-dom'
import { Home, CheckSquare, Calendar, Bot, MessageSquare, LayoutDashboard } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/chat', icon: MessageSquare, label: '对话' },
    { path: '/dashboard', icon: LayoutDashboard, label: '仪表板' },
    { path: '/tasks', icon: CheckSquare, label: '任务' },
    { path: '/schedules', icon: Calendar, label: '日程' },
    { path: '/agents', icon: Bot, label: 'Agents' },
  ]

  return (
    <div className="flex h-screen bg-slate-900">
      {/* 侧边栏 */}
      <aside className="w-64 bg-slate-800 border-r border-slate-700">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Bot className="w-8 h-8 text-primary-500" />
            Jarvis
          </h1>
          <p className="text-slate-400 text-sm mt-1">智能私人助手</p>
        </div>

        <nav className="px-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
