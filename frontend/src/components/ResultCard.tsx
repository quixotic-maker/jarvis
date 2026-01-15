import { ReactNode } from 'react'
import { Card, Badge, Button } from './ui'
import { LucideIcon, ExternalLink, Download, Share2 } from 'lucide-react'

export interface ResultCardProps {
  title: string
  subtitle?: string
  icon?: LucideIcon
  type?: 'data' | 'chart' | 'code' | 'file' | 'link' | 'info'
  children: ReactNode
  actions?: {
    label: string
    icon?: LucideIcon
    onClick: () => void
    variant?: 'primary' | 'secondary' | 'outline'
  }[]
  metadata?: { label: string; value: string }[]
  showShare?: boolean
  showDownload?: boolean
  onShare?: () => void
  onDownload?: () => void
}

const ResultCard = ({
  title,
  subtitle,
  icon: Icon,
  type = 'info',
  children,
  actions = [],
  metadata = [],
  showShare = false,
  showDownload = false,
  onShare,
  onDownload,
}: ResultCardProps) => {
  // 类型对应的颜色
  const typeColors = {
    data: 'emerald',
    chart: 'blue',
    code: 'purple',
    file: 'yellow',
    link: 'teal',
    info: 'slate',
  }

  const color = typeColors[type]

  return (
    <Card variant="glass" hoverable>
      {/* 头部 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3 flex-1">
          {/* 图标 */}
          {Icon && (
            <div className={`
              p-3 rounded-xl
              bg-${color}-500/10 border border-${color}-500/20
            `}>
              <Icon className={`w-6 h-6 text-${color}-400`} />
            </div>
          )}

          {/* 标题区 */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-white mb-1">
              {title}
            </h3>
            {subtitle && (
              <p className="text-sm text-slate-400">{subtitle}</p>
            )}
          </div>
        </div>

        {/* 类型标签 */}
        <Badge variant={color === 'emerald' ? 'success' : 'info'} size="sm">
          {type}
        </Badge>
      </div>

      {/* 元数据 */}
      {metadata.length > 0 && (
        <div className="flex flex-wrap gap-4 mb-4 pb-4 border-b border-slate-700">
          {metadata.map((item, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className="text-xs text-slate-500">{item.label}:</span>
              <span className="text-sm text-slate-300 font-medium">
                {item.value}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* 内容区 */}
      <div className="mb-4">
        {children}
      </div>

      {/* 底部操作栏 */}
      {(actions.length > 0 || showShare || showDownload) && (
        <div className="flex items-center justify-between pt-4 border-t border-slate-700">
          {/* 自定义操作 */}
          <div className="flex items-center gap-2">
            {actions.map((action, index) => {
              const ActionIcon = action.icon
              return (
                <Button
                  key={index}
                  variant={action.variant || 'outline'}
                  size="sm"
                  onClick={action.onClick}
                  leftIcon={ActionIcon ? <ActionIcon className="w-4 h-4" /> : undefined}
                >
                  {action.label}
                </Button>
              )
            })}
          </div>

          {/* 通用操作 */}
          <div className="flex items-center gap-2">
            {showShare && onShare && (
              <button
                onClick={onShare}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
                title="分享"
              >
                <Share2 className="w-4 h-4" />
              </button>
            )}
            {showDownload && onDownload && (
              <button
                onClick={onDownload}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
                title="下载"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}
    </Card>
  )
}

export default ResultCard
