import { Card, Badge, Tooltip } from './ui'
import { LucideIcon, Play, Settings, Info } from 'lucide-react'

export interface ToolCardProps {
  name: string
  description: string
  icon: LucideIcon
  category?: string
  isEnabled?: boolean
  isRunning?: boolean
  version?: string
  lastRun?: string
  onExecute?: () => void
  onConfigure?: () => void
  onToggle?: (enabled: boolean) => void
}

const ToolCard = ({
  name,
  description,
  icon: Icon,
  category,
  isEnabled = true,
  isRunning = false,
  version,
  lastRun,
  onExecute,
  onConfigure,
  onToggle,
}: ToolCardProps) => {
  return (
    <Card
      variant="glass"
      hoverable
      className={`
        transition-all duration-300
        ${!isEnabled ? 'opacity-60' : ''}
        ${isRunning ? 'ring-2 ring-blue-500/50' : ''}
      `}
    >
      <div className="flex items-start gap-4">
        {/* 图标 */}
        <div className={`
          p-3 rounded-xl shrink-0
          ${isRunning
            ? 'bg-blue-500/20 border border-blue-500/30'
            : 'bg-purple-500/20 border border-purple-500/30'
          }
        `}>
          <Icon className={`w-6 h-6 ${isRunning ? 'text-blue-400 animate-pulse' : 'text-purple-400'}`} />
        </div>

        {/* 内容区 */}
        <div className="flex-1 min-w-0">
          {/* 标题行 */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-semibold text-white truncate">
                  {name}
                </h3>
                {version && (
                  <Tooltip content={`版本 ${version}`}>
                    <Badge variant="default" size="sm">
                      v{version}
                    </Badge>
                  </Tooltip>
                )}
              </div>
              {category && (
                <Badge variant="purple" size="sm">
                  {category}
                </Badge>
              )}
            </div>

            {/* 状态切换 */}
            {onToggle && (
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={isEnabled}
                  onChange={(e) => onToggle(e.target.checked)}
                />
                <div className="
                  w-11 h-6 bg-slate-700
                  peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-500
                  rounded-full peer
                  peer-checked:after:translate-x-full
                  after:content-[''] after:absolute after:top-[2px] after:left-[2px]
                  after:bg-white after:rounded-full after:h-5 after:w-5
                  after:transition-all
                  peer-checked:bg-emerald-500
                "></div>
              </label>
            )}
          </div>

          {/* 描述 */}
          <p className="text-sm text-slate-400 line-clamp-2 mb-3">
            {description}
          </p>

          {/* 底部信息 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {lastRun && (
                <span className="text-xs text-slate-500">
                  最后运行: {lastRun}
                </span>
              )}
            </div>

            {/* 操作按钮 */}
            <div className="flex items-center gap-1">
              {onExecute && (
                <Tooltip content="执行工具">
                  <button
                    onClick={onExecute}
                    disabled={!isEnabled || isRunning}
                    className="
                      p-2 rounded-lg
                      bg-emerald-500/10 hover:bg-emerald-500/20
                      text-emerald-400 hover:text-emerald-300
                      disabled:opacity-50 disabled:cursor-not-allowed
                      transition-all duration-200
                    "
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </Tooltip>
              )}

              {onConfigure && (
                <Tooltip content="配置">
                  <button
                    onClick={onConfigure}
                    className="
                      p-2 rounded-lg
                      hover:bg-slate-700
                      text-slate-400 hover:text-white
                      transition-all duration-200
                    "
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </Tooltip>
              )}
            </div>
          </div>

          {/* 运行状态指示 */}
          {isRunning && (
            <div className="mt-3 flex items-center gap-2 p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              <span className="text-xs text-blue-400 font-medium">正在运行...</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

export default ToolCard
