import { useState } from 'react'
import { Button, Badge, Tooltip } from '../ui'
import {
  Search,
  Bell,
  Mic,
  Moon,
  Sun,
  Settings,
  ChevronDown,
} from 'lucide-react'

export interface TopNavProps {
  title?: string
  subtitle?: string
  showVoice?: boolean
  onVoiceClick?: () => void
}

const TopNav = ({
  title = 'Jarvis',
  subtitle,
  showVoice = true,
  onVoiceClick,
}: TopNavProps) => {
  const [isDark, setIsDark] = useState(true)
  const [notifications] = useState(3)
  const [isSearchFocused, setIsSearchFocused] = useState(false)

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-40">
      <div className="h-full px-6 flex items-center justify-between gap-4">
        {/* 左侧：标题 */}
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-white truncate">{title}</h1>
          {subtitle && (
            <p className="text-sm text-slate-400 truncate">{subtitle}</p>
          )}
        </div>

        {/* 中间：搜索框 */}
        <div className="flex-1 max-w-2xl">
          <div className={`
            relative transition-all duration-200
            ${isSearchFocused ? 'scale-105' : ''}
          `}>
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="搜索对话、Agent、工具... (Ctrl+K)"
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setIsSearchFocused(false)}
              className="
                w-full pl-12 pr-4 py-2.5 rounded-xl
                bg-slate-800 border border-slate-700
                text-white placeholder-slate-500
                focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent
                transition-all duration-200
              "
            />
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <kbd className="px-2 py-1 text-xs font-semibold text-slate-400 bg-slate-700 rounded border border-slate-600">
                ⌘K
              </kbd>
            </div>
          </div>
        </div>

        {/* 右侧：操作按钮 */}
        <div className="flex items-center gap-2">
          {/* 语音输入 */}
          {showVoice && (
            <Tooltip content="语音输入">
              <Button
                variant="ghost"
                size="sm"
                onClick={onVoiceClick}
                className="relative"
              >
                <Mic className="w-5 h-5" />
              </Button>
            </Tooltip>
          )}

          {/* 通知 */}
          <Tooltip content="通知">
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              {notifications > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-slate-900" />
              )}
            </Button>
          </Tooltip>

          {/* 主题切换 */}
          <Tooltip content={isDark ? '浅色模式' : '深色模式'}>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDark(!isDark)}
            >
              {isDark ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>
          </Tooltip>

          {/* 设置 */}
          <Tooltip content="设置">
            <Button variant="ghost" size="sm">
              <Settings className="w-5 h-5" />
            </Button>
          </Tooltip>

          {/* 分隔线 */}
          <div className="w-px h-6 bg-slate-700" />

          {/* 用户菜单 */}
          <button className="
            flex items-center gap-2 px-3 py-2 rounded-xl
            hover:bg-slate-800
            transition-all duration-200
          ">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
              <span className="text-sm font-bold text-white">L</span>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>
        </div>
      </div>
    </header>
  )
}

export default TopNav
