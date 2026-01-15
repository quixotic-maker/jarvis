import { Card, Badge, Avatar } from './ui'
import { Clock, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'

export interface AgentCardProps {
  name: string
  description: string
  icon?: string
  status?: 'idle' | 'thinking' | 'success' | 'error'
  category?: string
  lastActive?: string
  onClick?: () => void
  isActive?: boolean
}

const AgentCard = ({
  name,
  description,
  icon,
  status = 'idle',
  category,
  lastActive,
  onClick,
  isActive = false,
}: AgentCardProps) => {
  // 状态配置
  const statusConfig = {
    idle: {
      badge: { variant: 'default' as const, text: '待命中' },
      icon: null,
    },
    thinking: {
      badge: { variant: 'info' as const, text: '思考中', dot: true },
      icon: <Loader2 className="w-4 h-4 animate-spin text-blue-400" />,
    },
    success: {
      badge: { variant: 'success' as const, text: '已完成' },
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    },
    error: {
      badge: { variant: 'error' as const, text: '出错了' },
      icon: <AlertCircle className="w-4 h-4 text-red-400" />,
    },
  }

  const currentStatus = statusConfig[status]

  return (
    <Card
      variant={isActive ? 'glow' : 'glass'}
      hoverable
      onClick={onClick}
      className={`
        cursor-pointer transition-all duration-300
        ${isActive ? 'ring-2 ring-emerald-500/50' : ''}
      `}
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <Avatar
          src={icon}
          name={name}
          size="lg"
          status={status === 'thinking' ? 'busy' : status === 'idle' ? 'online' : undefined}
        />

        {/* 内容区 */}
        <div className="flex-1 min-w-0">
          {/* 标题行 */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-white mb-1 truncate">
                {name}
              </h3>
              {category && (
                <Badge variant="purple" size="sm">
                  {category}
                </Badge>
              )}
            </div>
            
            {/* 状态指示 */}
            <div className="flex items-center gap-2">
              {currentStatus.icon}
              <Badge
                variant={currentStatus.badge.variant}
                size="sm"
                dot={currentStatus.badge.dot}
              >
                {currentStatus.badge.text}
              </Badge>
            </div>
          </div>

          {/* 描述 */}
          <p className="text-sm text-slate-400 line-clamp-2 mb-3">
            {description}
          </p>

          {/* 底部信息 */}
          {lastActive && (
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Clock className="w-3 h-3" />
              <span>最后活跃: {lastActive}</span>
            </div>
          )}
        </div>
      </div>

      {/* 激活状态的光晕效果 */}
      {isActive && (
        <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl opacity-20 blur-xl -z-10 animate-pulse" />
      )}
    </Card>
  )
}

export default AgentCard
