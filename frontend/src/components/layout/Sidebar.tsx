import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Badge, Tooltip, Avatar } from '../ui'
import {
  MessageSquare,
  Brain,
  Users,
  Calendar,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
  TrendingUp,
  Book,
  Target,
  Plus,
} from 'lucide-react'

export interface SidebarProps {
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

const Sidebar = ({ isCollapsed = false, onToggleCollapse }: SidebarProps) => {
  const [activeCount] = useState(3) // 活跃Agent数量

  // 导航菜单配置
  const navItems = [
    {
      label: '对话',
      icon: MessageSquare,
      path: '/chat',
      badge: '2',
    },
    {
      label: '知识大脑',
      icon: Brain,
      path: '/brain',
      isNew: true,
    },
    {
      label: 'Agent中心',
      icon: Users,
      path: '/agents',
      badge: activeCount.toString(),
    },
    {
      label: '日程管理',
      icon: Calendar,
      path: '/schedule',
    },
    {
      label: '学习工作台',
      icon: Book,
      path: '/learning',
    },
    {
      label: '成长轨迹',
      icon: TrendingUp,
      path: '/growth',
    },
    {
      label: '目标管理',
      icon: Target,
      path: '/goals',
    },
    {
      label: '笔记',
      icon: FileText,
      path: '/notes',
    },
  ]

  const bottomItems = [
    {
      label: 'MCP工具',
      icon: Zap,
      path: '/tools',
      badge: '12',
    },
    {
      label: '设置',
      icon: Settings,
      path: '/settings',
    },
  ]

  return (
    <aside
      className={`
        relative flex flex-col h-screen
        bg-slate-900 border-r border-slate-800
        transition-all duration-300 ease-in-out
        ${isCollapsed ? 'w-20' : 'w-64'}
      `}
    >
      {/* Logo区域 */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gradient">Jarvis</h1>
              <p className="text-xs text-slate-500">第二大脑</p>
            </div>
          </div>
        )}

        {/* 折叠按钮 */}
        <button
          onClick={onToggleCollapse}
          className="
            p-2 rounded-lg
            hover:bg-slate-800
            text-slate-400 hover:text-white
            transition-all duration-200
          "
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* 快速创建 */}
      {!isCollapsed && (
        <div className="p-4">
          <button className="
            w-full flex items-center justify-center gap-2
            px-4 py-3 rounded-xl
            bg-gradient-to-r from-emerald-500 to-teal-500
            text-white font-medium
            hover:shadow-lg hover:shadow-emerald-500/25
            active:scale-95
            transition-all duration-200
          ">
            <Plus className="w-5 h-5" />
            <span>新建对话</span>
          </button>
        </div>
      )}

      {/* 主导航 */}
      <nav className="flex-1 overflow-y-auto px-3 py-2">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Tooltip
                key={item.path}
                content={item.label}
                position="right"
              >
                <NavLink
                  to={item.path}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2.5 rounded-xl
                    transition-all duration-200
                    ${isActive
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }
                    ${isCollapsed ? 'justify-center' : ''}
                  `}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 font-medium">{item.label}</span>
                      {item.badge && (
                        <Badge variant="success" size="sm">
                          {item.badge}
                        </Badge>
                      )}
                      {item.isNew && (
                        <Badge variant="warning" size="sm">
                          NEW
                        </Badge>
                      )}
                    </>
                  )}
                </NavLink>
              </Tooltip>
            )
          })}
        </div>
      </nav>

      {/* 底部导航 */}
      <div className="border-t border-slate-800 px-3 py-2">
        <div className="space-y-1 mb-3">
          {bottomItems.map((item) => {
            const Icon = item.icon
            return (
              <Tooltip
                key={item.path}
                content={item.label}
                position="right"
              >
                <NavLink
                  to={item.path}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2.5 rounded-xl
                    transition-all duration-200
                    ${isActive
                      ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }
                    ${isCollapsed ? 'justify-center' : ''}
                  `}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 font-medium">{item.label}</span>
                      {item.badge && (
                        <Badge variant="purple" size="sm">
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </NavLink>
              </Tooltip>
            )
          })}
        </div>

        {/* 用户信息 */}
        <div className={`
          flex items-center gap-3 p-3 rounded-xl
          bg-slate-800 border border-slate-700
          ${isCollapsed ? 'justify-center' : ''}
        `}>
          <Avatar
            name="用户"
            size="sm"
            status="online"
          />
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Liu</p>
              <p className="text-xs text-slate-500">liu@example.com</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
