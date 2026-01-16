import { LucideIcon, Inbox, FileQuestion, AlertCircle, Search } from 'lucide-react'
import { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  children?: ReactNode
}

const iconMap = {
  inbox: Inbox,
  notFound: FileQuestion,
  error: AlertCircle,
  search: Search,
}

export type EmptyStateType = keyof typeof iconMap

export default function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* 图标 */}
      <div className="w-24 h-24 mb-6 rounded-full bg-gray-800/50 flex items-center justify-center">
        <Icon className="w-12 h-12 text-gray-500" strokeWidth={1.5} />
      </div>

      {/* 标题 */}
      <h3 className="text-xl font-semibold text-gray-300 mb-2">{title}</h3>

      {/* 描述 */}
      {description && (
        <p className="text-gray-500 max-w-md mb-6">{description}</p>
      )}

      {/* 自定义内容 */}
      {children}

      {/* 操作按钮 */}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 shadow-lg shadow-blue-500/20"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

// 预定义的空状态类型
export function EmptyInbox({ action }: { action?: EmptyStateProps['action'] }) {
  return (
    <EmptyState
      icon={Inbox}
      title="暂无数据"
      description="这里还没有任何内容，开始创建第一条记录吧"
      action={action}
    />
  )
}

export function EmptySearch({ query }: { query?: string }) {
  return (
    <EmptyState
      icon={Search}
      title="未找到匹配结果"
      description={query ? `没有找到与 "${query}" 相关的内容` : '尝试使用不同的关键词搜索'}
    />
  )
}

export function EmptyError({ retry }: { retry?: () => void }) {
  return (
    <EmptyState
      icon={AlertCircle}
      title="加载失败"
      description="数据加载时出现了问题，请稍后重试"
      action={retry ? { label: '重试', onClick: retry } : undefined}
    />
  )
}

export function EmptyNotFound() {
  return (
    <EmptyState
      icon={FileQuestion}
      title="页面不存在"
      description="抱歉，您访问的页面不存在或已被移除"
    />
  )
}
