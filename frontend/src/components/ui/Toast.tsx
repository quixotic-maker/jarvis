import { useEffect } from 'react'
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface ToastProps {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  onClose: (id: string) => void
}

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
}

const colorMap = {
  success: 'from-emerald-500 to-teal-500',
  error: 'from-red-500 to-rose-500',
  info: 'from-blue-500 to-cyan-500',
  warning: 'from-orange-500 to-amber-500',
}

const bgColorMap = {
  success: 'bg-emerald-500/10 border-emerald-500/30',
  error: 'bg-red-500/10 border-red-500/30',
  info: 'bg-blue-500/10 border-blue-500/30',
  warning: 'bg-orange-500/10 border-orange-500/30',
}

export function Toast({ id, type, title, message, duration = 5000, onClose }: ToastProps) {
  const Icon = iconMap[type]

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id)
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [id, duration, onClose])

  return (
    <div
      className={`
        relative overflow-hidden rounded-xl border backdrop-blur-xl
        ${bgColorMap[type]}
        animate-in slide-in-from-right-full duration-300
        shadow-lg shadow-black/20
        min-w-[320px] max-w-md
      `}
    >
      {/* 渐变顶部边框 */}
      <div className={`h-1 bg-gradient-to-r ${colorMap[type]}`} />
      
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* 图标 */}
          <div className={`p-1 rounded-lg bg-gradient-to-br ${colorMap[type]} flex-shrink-0`}>
            <Icon className="w-5 h-5 text-white" />
          </div>

          {/* 内容 */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-white mb-0.5">{title}</h4>
            {message && (
              <p className="text-sm text-slate-300 break-words">{message}</p>
            )}
          </div>

          {/* 关闭按钮 */}
          <button
            onClick={() => onClose(id)}
            className="flex-shrink-0 text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 进度条 */}
      {duration > 0 && (
        <div className="h-1 bg-white/10">
          <div
            className={`h-full bg-gradient-to-r ${colorMap[type]}`}
            style={{
              animation: `shrink ${duration}ms linear forwards`,
            }}
          />
        </div>
      )}

      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </div>
  )
}
